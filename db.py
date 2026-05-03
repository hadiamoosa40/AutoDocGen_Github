import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    print("⚠️ MONGODB_URI not set, using in-memory storage")
    client = None
else:
    client = MongoClient(MONGO_URI)
    db = client["github_integration"]
    users_collection = db["users"]

# In-memory fallback
memory_store = {}

def get_user(github_id):
    if client:
        return users_collection.find_one({"github_id": github_id})
    return memory_store.get(str(github_id))

def save_user(github_id, user_data):
    if client:
        users_collection.update_one(
            {"github_id": github_id},
            {"$set": user_data},
            upsert=True
        )
    else:
        memory_store[str(github_id)] = user_data
    print(f"✅ User saved: {github_id}")

def update_user(github_id, update_data):
    if client:
        users_collection.update_one(
            {"github_id": github_id},
            {"$set": update_data}
        )
    else:
        if str(github_id) in memory_store:
            memory_store[str(github_id)].update(update_data)
    print(f"✅ User updated: {github_id}")