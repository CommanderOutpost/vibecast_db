# apps/users/main.py
#
# FastAPI service exposing user-centric endpoints.
# All the heavy logic lives in libs/users/service.py.

from fastapi import FastAPI, Request, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from libs.users import service
from libs.users.utils import jwt, settings  # for auth dependency

app = FastAPI(title="Users Service")

# ---------------------------------------------------------------------------
# request/response models
# ---------------------------------------------------------------------------


class SignupBody(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class ChannelBody(BaseModel):
    channel_id: str
    is_owner: bool = False


# ---------------------------------------------------------------------------
# tiny JWT auth dependency to identify the caller when needed
# ---------------------------------------------------------------------------


def get_current_user_id(
    token: str = Depends(
        lambda authorization: authorization.headers.get("Authorization")
    ),
):
    """
    Very small helper that decodes our own JWT and returns the user’s id.
    Expects header:  Authorization: Bearer <jwt>
    """
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token"
        )
    _, jwt_token = token.split(" ", 1)
    try:
        payload = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload["sub"]


# ---------------------------------------------------------------------------
# public endpoints
# ---------------------------------------------------------------------------


@app.post("/signup", status_code=201)
async def signup(body: SignupBody):
    jwt_token = await service.signup(body.username, body.email, body.password)
    return {"access_token": jwt_token, "token_type": "bearer"}


@app.post("/login")
async def login(body: LoginBody):
    jwt_token = await service.login(body.email, body.password)
    return {"access_token": jwt_token, "token_type": "bearer"}


@app.get("/auth/google/login")
async def google_login(request: Request):
    """
    Generates the Google consent-screen URL and redirects the browser there.
    """
    redirect_uri = str(request.url_for("google_callback"))
    return await service.get_google_login_url(request, redirect_uri)


@app.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request):
    """
    Google calls this after the user grants permission.
    We exchange the code, create/lookup the user, then hand back our JWT.
    """
    redirect_uri = str(request.url_for("google_callback"))
    jwt_token = await service.handle_google_callback(request, redirect_uri)
    return {"access_token": jwt_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# channel management (requires auth)
# ---------------------------------------------------------------------------


@app.post("/channels/subscribe")
async def subscribe_channel(
    body: ChannelBody, user_id: str = Depends(get_current_user_id)
):
    await service.subscribe_channel(user_id, body.channel_id, body.is_owner)
    return {"detail": "subscribed"}


@app.post("/channels/unsubscribe")
async def unsubscribe_channel(
    body: ChannelBody, user_id: str = Depends(get_current_user_id)
):
    await service.unsubscribe_channel(user_id, body.channel_id)
    return {"detail": "unsubscribed"}


@app.get("/channels/mine")
async def my_channels(user_id: str = Depends(get_current_user_id)):
    channels = await service.get_my_channels(user_id)
    return {"channels": channels}
