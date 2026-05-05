import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

client = MongoClient(MONGO_URI)
db = client["github_integration"]
users_collection = db["users"]
tokens_collection = db["tokens"]

