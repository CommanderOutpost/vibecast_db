from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # MongoDB config for chat/presence
    MONGO_URI: str
    MONGO_DB: str

    # Redis config for presence tracking
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # External API keys
    YOUTUBE_API_KEY: str

    # Google OAuth credentials (optional)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # JWT and session keys
    JWT_SECRET_KEY: str
    SESSION_SECRET_KEY: str

    # Celery broker/backend
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_BACKEND_URL: Optional[str] = None

    model_config = ConfigDict(
        env_file=".env",
    )


settings = Settings()
