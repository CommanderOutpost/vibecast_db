from typing import Dict, List
from fastapi import Request, HTTPException, status
from pydantic import EmailStr
from bson import ObjectId

from config.config import settings
from libs.database.users import (
    create_google_user,
    create_user as db_create_user,
    get_user_by_email as db_get_user_by_email,
    add_channel_to_user as db_add_channel,
    get_user_by_google_id,
    remove_channel_from_user as db_remove_channel,
    list_user_channels as db_list_channels,
    add_channel_to_user as db_add_channel,
    subscribe_user_to_channel,
    delete_user as db_delete_user,
)
from libs.users.utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_google_authorization_url,
    exchange_google_code,
)

from libs.database.youtube.channels import (
    get_channel_by_youtube_id as db_get_channel_by_youtube_id,
    create_channel as db_create_channel,
    get_channel_by_id as db_get_channel_by_id,
    upsert_channel,
)
from libs.youtube.get_youtube_channel_info import get_channel_info_by_handle


async def signup(username: str, email: EmailStr, password: str) -> str:
    """
    Register a new user: hash their password, store them,
    and return a signed JWT on success.
    """
    if await db_get_user_by_email(email):
        raise ValueError("Email already registered")

    pwd_hash = hash_password(password)
    user_id = await db_create_user(username, email, pwd_hash)
    return create_access_token({"sub": user_id})


async def login(email: EmailStr, password: str) -> str:
    """
    Authenticate an existing user and return a JWT.
    """
    user = await db_get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Username or password is incorrect")

    return create_access_token({"sub": str(user["_id"])})


async def subscribe_channel(user_id: str, handle: str, is_owner: bool = False) -> dict:
    # fetch full metadata from YouTube
    try:
        resource = get_channel_info_by_handle(handle, api_key=settings.YOUTUBE_API_KEY)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # shape it exactly for Mongo
    channel_data = {
        "name": resource["snippet"]["title"],
        "youtube_channel_id": resource["id"],
        "kind": resource["kind"],
        "etag": resource["etag"],
        "snippet": resource["snippet"],
        "contentDetails": resource["contentDetails"],
        "statistics": {
            "viewCount": int(resource["statistics"]["viewCount"]),
            "subscriberCount": int(resource["statistics"]["subscriberCount"]),
            "hiddenSubscriberCount": resource["statistics"]["hiddenSubscriberCount"],
            "videoCount": int(resource["statistics"]["videoCount"]),
        },
    }

    # upsert via the new DB helper, get back a string ID
    channel_id = await upsert_channel(channel_data)

    # attempt to subscribe the user; if False, they were already subscribed
    added = await subscribe_user_to_channel(user_id, channel_id, is_owner)
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You’re already subscribed to this channel.",
        )

    # fetch the full channel doc and convert _id → id
    saved = await db_get_channel_by_id(channel_id)
    raw_id = saved.pop("_id", None)
    if raw_id:
        saved["id"] = str(raw_id)

    return saved


async def unsubscribe_channel(user_id: str, mongo_channel_id: str):
    """
    Remove a channel subscription from the user's profile.
    Expects the Mongo document _id for the channel.
    """

    try:
        ObjectId(mongo_channel_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel ID: {mongo_channel_id!r}",
        )

    # Delegate to the DB helper
    await db_remove_channel(user_id, mongo_channel_id)


async def get_my_channels(user_id: str) -> List[dict]:
    """
    List all channels the user is subscribed to, along with ownership flags.
    """
    raw = await db_list_channels(user_id)
    # turn ObjectId into str for JSON
    return [
        {"channel_id": str(entry["channel_id"]), "is_owner": entry["is_owner"]}
        for entry in raw
    ]


async def get_google_login_url(request: Request, redirect_uri: str) -> str:
    """
    Kick off the OAuth dance.
    """
    return await get_google_authorization_url(request, redirect_uri)


async def handle_google_callback(request) -> str:
    """
    Runs on /auth/google/callback.
    Looks up or creates the user, then issues our own JWT.
    """
    info = await exchange_google_code(request)

    user = await get_user_by_google_id(info["google_id"])
    if not user:
        user_id = await create_google_user(
            username=info["username"],
            email=info["email"],
            google_id=info["google_id"],
        )
    else:
        user_id = str(user["_id"])

    return create_access_token({"sub": user_id})


async def get_channel_info(channel_id: str) -> dict:
    """
    Fetch the full channel document from Mongo by its _id,
    convert ObjectId → str, and return everything else intact.
    """
    # validate the ID
    try:
        ObjectId(channel_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel_id {channel_id!r}",
        )

    doc = await db_get_channel_by_id(channel_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id!r} not found",
        )

    # convert _id → id
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)

    return doc


async def delete_account(user_id: str) -> None:
    """
    Remove a user and all their subscriptions (the 'channels' array).
    """
    # No need to explicitly remove subscriptions anywhere else,
    # since they're stored only in the user's document.
    deleted = await db_delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id!r} not found or already deleted",
        )
