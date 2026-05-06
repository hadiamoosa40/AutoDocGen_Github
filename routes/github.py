from fastapi import APIRouter
from bson import ObjectId
import httpx

from db import users
from services.github_app import get_installation_token

router = APIRouter()

# GET REPOS
@router.get("/repos")
async def repos(uid: str):
    user = await users.find_one({"_id": ObjectId(uid)})
    print("USER:", user)

    if not user or not user.get("installation_id"):
        return {"error": "GitHub App not installed"}

    token = await get_installation_token(user["installation_id"])

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/installation/repositories",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()