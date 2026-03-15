from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client: AsyncIOMotorClient | None = None


async def get_db():
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongodb_uri)
    return client[settings.db_name]


async def close_db():
    global client
    if client:
        client.close()
        client = None
