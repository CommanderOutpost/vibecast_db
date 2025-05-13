from config.database import db
from bson import ObjectId
from typing import List


async def create_user(username: str, email: str, password_hash: str) -> str:
    """
    Inserts a new user document.
    """
    result = await db.users.insert_one(
        {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "channels": [],
        }
    )
    return str(result.inserted_id)


async def get_user_by_email(email: str):
    """
    Finds a user by their email address.
    """
    return await db.users.find_one({"email": email})


async def get_user_by_id(user_id: str):
    """
    Finds a user by their MongoDB _id.
    """
    return await db.users.find_one({"_id": ObjectId(user_id)})


async def add_channel_to_user(user_id: str, channel_id: str, is_owner: bool):
    """
    Pushes a {channel_id, is_owner} entry into the user's channels array,
    if not already present.
    """
    await db.users.update_one(
        {
            "_id": ObjectId(user_id),
            "channels.channel_id": {"$ne": ObjectId(channel_id)},
        },
        {
            "$push": {
                "channels": {"channel_id": ObjectId(channel_id), "is_owner": is_owner}
            }
        },
    )


async def remove_channel_from_user(user_id: str, channel_id: str):
    """
    Pulls any matching channel_id entry out of the user's channels array.
    """
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"channels": {"channel_id": ObjectId(channel_id)}}},
    )


async def list_user_channels(user_id: str) -> List[dict]:
    """
    Returns the raw channels array for a user.
    """
    doc = await db.users.find_one({"_id": ObjectId(user_id)}, {"channels": 1})
    return doc.get("channels", []) if doc else []


async def get_user_by_google_id(google_id: str):
    """
    Find a user document by its Google account ID.
    """
    return await db.users.find_one({"google_id": google_id})


async def create_google_user(username: str, email: str, google_id: str) -> str:
    """
    Inserts a new user created via Google OAuth.
    """
    result = await db.users.insert_one(
        {
            "username": username,
            "email": email,
            "google_id": google_id,
            "password_hash": None,
            "channels": [],
        }
    )
    return str(result.inserted_id)
