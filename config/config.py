from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from openai import OpenAI


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
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OPENAI_API_KEY: str

    # JWT and session keys
    JWT_SECRET_KEY: str
    SESSION_SECRET_KEY: str

    # Celery broker/backend
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_BACKEND_URL: Optional[str] = None
    
    # Service URLs
    USERS_SERVICE_URL: str
    YOUTUBE_SERVICE_URL: str
    AGENTS_SERVICE_URL: str

    model_config = ConfigDict(
        env_file=".env",
    )


settings = Settings()

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)