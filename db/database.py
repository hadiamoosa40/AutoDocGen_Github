import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_db():
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "github_integ")

    if not mongo_uri:
        raise RuntimeError("MONGODB_URI environment variable is not set!")

    db_instance.client = AsyncIOMotorClient(mongo_uri)
    db_instance.db = db_instance.client[db_name]
    print(f"✅ Connected to MongoDB: {db_name}")

    await db_instance.db.users.create_index("github_id", unique=True)
    await db_instance.db.users.create_index("username")
    await db_instance.db.tokens.create_index("user_id")
    await db_instance.db.tokens.create_index("jti", unique=True)
    await db_instance.db.webhooks.create_index("repo_full_name")
    await db_instance.db.webhooks.create_index("user_id")
    print("✅ MongoDB indexes created")


async def disconnect_db():
    if db_instance.client:
        db_instance.client.close()
        print("🔌 Disconnected from MongoDB")


def get_db():
    return db_instance.db