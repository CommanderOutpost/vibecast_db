from typing import List
from fastapi import Request
from pydantic import EmailStr

from config.config import settings
from libs.database.users import (
    create_google_user,
    create_user as db_create_user,
    get_user_by_email as db_get_user_by_email,
    add_channel_to_user as db_add_channel,
    get_user_by_google_id,
    remove_channel_from_user as db_remove_channel,
    list_user_channels as db_list_channels,
)
from libs.users.utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_google_authorization_url,
    exchange_google_code,
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


async def subscribe_channel(user_id: str, channel_id: str, is_owner: bool = False):
    """
    Add a channel subscription (with ownership flag) to the user's profile.
    """
    await db_add_channel(user_id, channel_id, is_owner)


async def unsubscribe_channel(user_id: str, channel_id: str):
    """
    Remove a channel subscription from the user's profile.
    """
    await db_remove_channel(user_id, channel_id)


async def get_my_channels(user_id: str) -> List[dict]:
    """
    List all channels the user is subscribed to, along with ownership flags.
    """
    return await db_list_channels(user_id)


async def get_google_login_url(request: Request, redirect_uri: str) -> str:
    """
    Kick off the OAuth dance.
    """
    return await get_google_authorization_url(request, redirect_uri)


async def handle_google_callback(request: Request, redirect_uri: str) -> str:
    """
    Called after Google redirects back with a code.
    Creates or fetches the user, then issues our JWT.
    """
    info = await exchange_google_code(request, redirect_uri)
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
