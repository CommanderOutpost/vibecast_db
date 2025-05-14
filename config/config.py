from pydantic_settings import BaseSettings


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

    # JWT and session keys
    JWT_SECRET_KEY: str
    SESSION_SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
