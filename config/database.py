from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config.env import settings
from models.subscription import Subscription
from models.user import User

client: AsyncIOMotorClient | None = None

async def connect_to_database():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User, Subscription]) # Models to be added here
    print("Connected to MongoDB")

async def close_database_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

