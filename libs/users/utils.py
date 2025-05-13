import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from config.config import settings
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# load Google creds from env
_env = Config(".env")
GOOGLE_CLIENT_ID = _env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _env("GOOGLE_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def hash_password(password: str) -> str:
    """
    Hash a plain‐text password with bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plain‐text password against the stored bcrypt hash.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Produce a JWT including `data` as payload under 'sub', signed with our secret.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


async def get_google_authorization_url(request, redirect_uri: str) -> str:
    """
    Returns the URL to redirect the user to Google’s OAuth consent screen.
    """
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def exchange_google_code(request, redirect_uri: str) -> dict:
    """
    Exchange the callback code for tokens+userinfo.
    Returns: {"google_id", "email", "username"}.
    """
    token = await oauth.google.authorize_access_token(request, redirect_uri)
    userinfo = await oauth.google.parse_id_token(request, token)
    return {
        "google_id": userinfo["sub"],
        "email": userinfo["email"],
        "username": userinfo.get("name") or userinfo["email"].split("@")[0],
    }
