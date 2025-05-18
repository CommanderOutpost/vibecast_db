from config.database import db
from bson import ObjectId


async def create_channel(channel_data: dict) -> str:

    result = await db.channels.insert_one(channel_data)
    return str(result.inserted_id)


async def get_channel_by_youtube_id(youtube_channel_id: str):
    return await db.channels.find_one({"youtube_channel_id": youtube_channel_id})


async def get_channel_by_id(channel_id: str):
    return await db.channels.find_one({"_id": ObjectId(channel_id)})


async def upsert_channel(channel_data: dict) -> str:
    """
    Insert or update a YouTube channel document by its youtube_channel_id.
    Returns the string _id of the upserted or existing document.
    """
    result = await db.channels.update_one(
        {"youtube_channel_id": channel_data["youtube_channel_id"]},
        {"$set": channel_data},
        upsert=True,
    )

    # If a new document was created, update_one.upserted_id holds its ObjectId
    if result.upserted_id:
        return str(result.upserted_id)

    # Otherwise fetch the existing doc to get its _id
    doc = await db.channels.find_one(
        {"youtube_channel_id": channel_data["youtube_channel_id"]}
    )
    return str(doc["_id"])
