from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB config for chat/presence
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "zance1"

    # Redis config for presence tracking
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1  # separate DB from your OTP microservice

    # JWT
    JWT_SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY"

    class Config:
        env_file = ".env"


settings = Settings()
