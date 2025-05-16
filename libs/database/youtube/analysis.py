from config.database import db
from bson import ObjectId


async def create_analysis(
    comment_id: str,
    sentiments: dict,
    major_discussions: dict,
    other_insights: list,
    video_requests: list,
) -> str:
    """
    Inserts a new comment-analysis document.
    """
    doc = {
        "comment_id": ObjectId(comment_id),
        "analysis": {
            "sentiments": sentiments,
            "major_discussions": major_discussions,
            "other_insights": other_insights,
            "video_requests": video_requests,
        },
    }
    result = await db.comment_analysis.insert_one(doc)
    return str(result.inserted_id)


async def update_analysis(
    comment_id: str,
    sentiments: dict,
    major_discussions: dict = None,
    other_insights: list = None,
    video_requests: list = None,
) -> int:
    """
    Updates fields of an existing comment-analysis doc.
    Only non-None parameters are set. Returns modified count.
    """
    update_fields = {}
    if sentiments is not None:
        update_fields["analysis.sentiments"] = sentiments
    if major_discussions is not None:
        update_fields["analysis.major_discussions"] = major_discussions
    if other_insights is not None:
        update_fields["analysis.other_insights"] = other_insights
    if video_requests is not None:
        update_fields["analysis.video_requests"] = video_requests

    if not update_fields:
        return 0

    result = await db.comment_analysis.update_one(
        {"comment_id": ObjectId(comment_id)}, {"$set": update_fields}
    )
    return result.modified_count


async def get_analysis_by_comment_id(comment_id: str):
    """
    Retrieves the analysis document for a given comment_id.
    """
    return await db.comment_analysis.find_one({"comment_id": ObjectId(comment_id)})
