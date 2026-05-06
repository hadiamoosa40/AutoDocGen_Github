from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
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
            raise ValueError("MONGODB_URI environment variable is not set")
        
        cls.client = AsyncIOMotorClient(uri)
        cls.db = cls.client["github_integ"]
        
        # Create indexes
        await cls.create_indexes()
        print("✅ Connected to MongoDB")
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("✅ Disconnected from MongoDB")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes"""
        # Users collection indexes
        await cls.db.users.create_indexes([
            IndexModel([("github_id", ASCENDING)], unique=True),
            IndexModel([("username", ASCENDING)]),
            IndexModel([("access_token", ASCENDING)]),
        ])
        
        # Repositories collection indexes
        await cls.db.repositories.create_indexes([
            IndexModel([("repo_id", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("full_name", ASCENDING)]),
        ])
        
        # Webhook events collection
        await cls.db.webhook_events.create_indexes([
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("event_type", ASCENDING)]),
        ])

# Database collections
async def get_users_collection():
    return Database.db["users"]

async def get_repositories_collection():
    return Database.db["repositories"]

async def get_webhook_events_collection():
    return Database.db["webhook_events"]