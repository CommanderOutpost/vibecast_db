from config.database import db
from bson import ObjectId


async def create_channel(name: str, youtube_channel_id: str):
    result = await db.channels.insert_one(
        {"name": name, "youtube_channel_id": youtube_channel_id}
    )
    return str(result.inserted_id)


async def get_channel_by_youtube_id(youtube_channel_id: str):
    return await db.channels.find_one({"youtube_channel_id": youtube_channel_id})
