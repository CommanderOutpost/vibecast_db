# apps/youtube/main.py
#
# REST façade for YouTube crawling.  Heavy work is deferred to Celery
# so that client requests return fast.

from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from bson import ObjectId
from libs.database.youtube.channels import (
    get_channel_by_youtube_id,
    get_channel_by_id,
    create_channel,
)
from libs.database.youtube.videos import get_videos_by_channel_id
from libs.tasks_youtube import enqueue_sync_channel, enqueue_grab_comments
from libs.youtube.service import get_channel_info  # Celery wrappers

app = FastAPI(title="YouTube Service")

# ---------------------------------------------------------------------------
# Pydantic DTOs
# ---------------------------------------------------------------------------


class SyncBody(BaseModel):
    channel_id: str


@app.post("/channels/sync", status_code=202)
async def sync_channel(body: SyncBody, background: BackgroundTasks):
    """
    Kick off a crawl of *all* videos for the given YouTube channel ID.
    We look up (or create) our Channel record, then enqueue the Celery task
    with both the remote ID and our Mongo ID.
    """
    # find existing Channel doc by YouTube ID
    ch = await get_channel_by_id(body.channel_id)
    channel_id = ch["_id"] if ch else None

    # dispatch the Celery task with both args
    background.add_task(
        enqueue_sync_channel,
        channel_id,
    )

    return {
        "detail": "sync queued",
        "channel_id": str(channel_id),
    }


@app.get("/channels/{channel_id}", status_code=200)
async def read_channel(channel_id: str):
    """
    Return the full channel document (including snippet, statistics, etc)
    for the given Mongo _id.
    """
    channel = await get_channel_info(channel_id)
    return channel


@app.get("/channels/{channel_id}/videos")
async def list_videos(channel_id: str):
    try:
        ObjectId(channel_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid channel_id")

    raw_videos = await get_videos_by_channel_id(channel_id)

    videos = []
    for v in raw_videos:
        videos.append(
            {
                "id": str(v["_id"]),
                "name": v.get("name"),
                "description": v.get("description"),
                "youtube_video_id": v.get("youtube_video_id"),
                "channel_id": str(v.get("channel_id")),
                "publish_time": v.get("publish_time"),
                "view_count": v.get("view_count"),
                "like_count": v.get("like_count"),
                "comment_count": v.get("comment_count"),
                "duration": v.get("duration"),
            }
        )

    return {"videos": videos}


@app.post("/videos/{video_id}/comments", status_code=202)
async def grab_comments(
    video_id: str, limit: int = 100, background: BackgroundTasks = None
):
    """
    Queue a background task to fetch (or refresh) top-level comments.
    """
    if background is None:  # FastAPI guarantees it, but mypy silencer
        background = BackgroundTasks()
    background.add_task(enqueue_grab_comments, video_id=video_id, limit=limit)
    return {"detail": "comment crawl queued", "video_id": video_id}
