from config.database import db
from bson import ObjectId


async def create_comments(video_id: str, comments: list):
    result = await db.comments.insert_one(
        {"video_id": ObjectId(video_id), "comments": comments}
    )
    return str(result.inserted_id)


async def get_comments_by_video_id(video_id: str):
    return await db.comments.find_one({"video_id": ObjectId(video_id)})
