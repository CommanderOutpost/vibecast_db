from typing import List
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
)


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
        raise ValueError("Invalid credentials")

    return create_access_token({"sub": str(user["_id"])})


async def subscribe_channel(
    user_id: str, youtube_channel_id: str, is_owner: bool = False
):
    """
    Subscribe the user to a YouTube channel. If the channel document
    doesn’t exist yet, create it first.
    """
    # 1) find or create the channel doc
    ch = await db_get_channel_by_youtube_id(youtube_channel_id)
    if not ch:
        # we don’t know the channel name here, so just store the ID as name
        mongo_id = await db_create_channel(
            name=youtube_channel_id, youtube_channel_id=youtube_channel_id
        )
    else:
        mongo_id = str(ch["_id"])

    # 2) add to the user's channels array
    await db_add_channel(user_id, mongo_id, is_owner)


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
