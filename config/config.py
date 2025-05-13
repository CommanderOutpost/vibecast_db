from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB config for chat/presence
    MONGO_URI: str
    MONGO_DB: str

    # Redis config for presence tracking
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # JWT
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
