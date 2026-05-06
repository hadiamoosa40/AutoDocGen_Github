from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        uri = os.getenv("MONGODB_URI")
        if not uri:
            print("⚠️ MONGODB_URI not set, using mock database")
            cls.db = None
            return
        
        try:
            cls.client = AsyncIOMotorClient(uri)
            cls.db = cls.client["github_integ"]
            
            # Create indexes
            await cls.create_indexes()
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            cls.db = None
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("✅ Disconnected from MongoDB")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes"""
        if not cls.db:
            return
        
        try:
            # Users collection indexes
            await cls.db.users.create_indexes([
                IndexModel([("github_id", ASCENDING)], unique=True),
                IndexModel([("username", ASCENDING)]),
            ])
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Index creation error: {e}")

# Database collections
async def get_users_collection():
    if Database.db:
        return Database.db["users"]
    return None

async def get_repositories_collection():
    if Database.db:
        return Database.db["repositories"]
    return None

async def get_webhook_events_collection():
    if Database.db:
        return Database.db["webhook_events"]
    return None