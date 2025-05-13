from config.database import db
from bson import ObjectId

async def create_video(name: str, youtube_video_id: str, channel_id: str):
    result = await db.videos.insert_one(
        {
            "name": name,
            "youtube_video_id": youtube_video_id,
            "channel_id": ObjectId(channel_id),
        }
    )
    return str(result.inserted_id)


async def get_videos_by_channel_id(channel_id: str):
    cursor = db.videos.find({"channel_id": ObjectId(channel_id)})
    return [video async for video in cursor]
