# apps/users/main.py
#
# FastAPI service exposing user-centric endpoints.
# All the heavy logic lives in libs/users/service.py.

from fastapi import FastAPI, Header, Request, HTTPException, Depends, status
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, EmailStr
from libs.users import service
from config.config import settings
from jose import jwt as jose_jwt
from jose.exceptions import JWTError

app = FastAPI(title="Users Service")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
)

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


class SubscribeBody(BaseModel):
    handle: str
    is_owner: bool = False


class ChannelBody(BaseModel):
    channel_id: str
    is_owner: bool = False


# ---------------------------------------------------------------------------
# tiny JWT auth dependency to identify the caller when needed
# ---------------------------------------------------------------------------


def get_current_user_id(
    authorization: str = Header(..., description="Bearer <token>")
) -> str:
    """
    Expects header: Authorization: Bearer <jwt>
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jose_jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload["sub"]


# ---------------------------------------------------------------------------
# public endpoints
# ---------------------------------------------------------------------------


@app.post("/signup", status_code=201)
async def signup(body: SignupBody):
    try:
        jwt_token = await service.signup(body.username, body.email, body.password)
        return {"access_token": jwt_token, "token_type": "bearer"}
    except ValueError as e:
        # duplicate email → 409 Conflict
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@app.post("/login")
async def login(body: LoginBody):
    try:
        jwt_token = await service.login(body.email, body.password)
        return {"access_token": jwt_token, "token_type": "bearer"}
    except ValueError as e:
        # invalid credentials → 401 Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.delete("/me", status_code=204)
async def delete_account(user_id: str = Depends(get_current_user_id)):
    """
    Delete the authenticated user's account, along with all their subscriptions.
    """
    try:
        await service.delete_account(user_id)
    except HTTPException as e:
        # If user not found or any other error, propagate
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))


@app.get("/auth/google/login")
async def google_login(request: Request):
    try:
        redirect_uri = str(request.url_for("google_callback"))
        return await service.get_google_login_url(request, redirect_uri)
    except ValueError as e:
        # any oauth error → 400 Bad Request
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request):
    """
    Google lands here after the consent screen.
    We just hand the Request to our service layer.
    """
    try:
        jwt_token = await service.handle_google_callback(request)
        return {"access_token": jwt_token, "token_type": "bearer"}
    except ValueError as e:
        # nice 400 instead of 500 on logical issues
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ---------------------------------------------------------------------------
# channel management (requires auth)
# ---------------------------------------------------------------------------


@app.post("/channels/subscribe")
async def subscribe_channel(
    body: SubscribeBody, user_id: str = Depends(get_current_user_id)
):
    try:
        channel = await service.subscribe_channel(user_id, body.handle, body.is_owner)
        return {"channel": channel}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/channels/unsubscribe")
async def unsubscribe_channel(
    body: ChannelBody, user_id: str = Depends(get_current_user_id)
):
    try:
        await service.unsubscribe_channel(user_id, body.channel_id)
        return {"detail": "unsubscribed"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/channels/mine")
async def my_channels(user_id: str = Depends(get_current_user_id)):
    try:
        channels = await service.get_my_channels(user_id)
        return {"channels": channels}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
