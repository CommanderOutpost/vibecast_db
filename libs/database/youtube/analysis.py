from bson import ObjectId
from config.database import db
from typing import Dict, List


def _build_doc(
    comment_id: str,
    sentiments: Dict,
    headline: str,
    discussions: Dict,
    people: List[Dict],
    other_insights: List[str],
    video_requests: List[str],
):
    return {
        "comment_id": ObjectId(comment_id),
        "analysis": {
            "sentiments": sentiments,
            "headline": headline,
            "discussions": discussions,
            "people": people,
            "other_insights": other_insights,
            "video_requests": video_requests,
        },
    }


async def create_analysis(**kwargs) -> str:
    """
    Insert a new analysis doc; kwargs match _build_doc() signature.
    """
    doc = _build_doc(**kwargs)
    res = await db.comment_analysis.insert_one(doc)
    return str(res.inserted_id)


async def update_analysis(comment_id: str, **fields) -> int:
    """
    Patch only the provided top-level keys inside analysis.* .
    """
    update_set = {f"analysis.{k}": v for k, v in fields.items()}
    if not update_set:
        return 0
    res = await db.comment_analysis.update_one(
        {"comment_id": ObjectId(comment_id)}, {"$set": update_set}
    )
    return res.modified_count


async def get_analysis_by_comment_id(comment_id: str):
    return await db.comment_analysis.find_one({"comment_id": ObjectId(comment_id)})
