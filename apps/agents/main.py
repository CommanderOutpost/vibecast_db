from typing import Any, Dict, List
from fastapi import BackgroundTasks, FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from bson import ObjectId

from libs.database.youtube.analysis import get_analysis_by_comment_id
from libs.tasks_agents import enqueue_analyze_comments
from libs.database.youtube.videos import get_video_by_id
from libs.database.youtube.comments import get_comments_by_video_id
from libs.users.service import get_my_channels
from apps.users.main import get_current_user_id  # JWT auth
from libs.schema.youtube.analysis_schema import AnalysisSchema

app = FastAPI(title="Agents Service")


class AnalyzeResponse(BaseModel):
    result: str


class VideoAnalysisResponse(BaseModel):
    id: str
    comment_id: str
    sentiments: Dict[str, int]
    headline: str
    discussions: Dict[str, List[str]]
    people: List[Dict[str, Any]]
    other_insights: List[str]
    video_requests: List[str]


async def _verify_video_access(user_id: str, video_id: str) -> None:
    """
    Throws an HTTPException if the user is not allowed to analyze this video.
    """
    # 1) malformed ID?
    try:
        ObjectId(video_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video_id {video_id!r}",
        )

    # 2) must exist
    video = await get_video_by_id(video_id)
    print(video)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id!r} not found",
        )

    # 3) comments must exist
    comments_doc = await get_comments_by_video_id(video_id)
    if not comments_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No comments fetched yet; queue comments first.",
        )

    # 4) only owners may analyze
    user_channels = await get_my_channels(user_id)
    owner_ids = {c["channel_id"] for c in user_channels}
    if video["channel_id"] not in owner_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this video.",
        )


@app.post(
    "/analyze-comments/{video_id}",
    response_model=AnalyzeResponse,
    status_code=202,
)
async def analyze_comments_route(
    video_id: str,
    background: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    # perform all our checks
    await _verify_video_access(user_id, video_id)

    # enqueue and return
    background.add_task(enqueue_analyze_comments, video_id)
    return {"result": f"analysis queued for {video_id}"}


@app.get(
    "/analysis/{video_id}",
    response_model=VideoAnalysisResponse,
)
async def get_analysis_route(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
):
    # Same ownership / existence guard as before
    await _verify_video_access(user_id, video_id)

    doc = await get_analysis_by_comment_id(video_id)
    if not doc or not doc.get("analysis"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found"
        )

    a = doc["analysis"]

    # Fallback for any legacy docs that still have "major_discussions"
    discussions = (
        a.get("discussions")
        or a.get("major_discussions")
        or {"video": [], "creator": [], "topic": []}
    )

    return {
        "id": str(doc["_id"]),
        "comment_id": str(doc["comment_id"]),
        "sentiments": a.get("sentiments"),
        "headline": a.get("headline", ""),
        "discussions": discussions,
        "people": a.get("people", []),
        "other_insights": a.get("other_insights", []),
        "video_requests": a.get("video_requests", []),
    }
