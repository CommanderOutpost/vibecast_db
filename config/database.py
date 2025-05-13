from motor.motor_asyncio import AsyncIOMotorClient
from config.config import settings

MONGO_URI = settings.MONGO_URI
MONGO_DB = settings.MONGO_DB
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
