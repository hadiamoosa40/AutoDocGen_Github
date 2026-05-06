from fastapi import APIRouter
from db import users
from services.github_app_service import *

router = APIRouter()

@router.post("/install")
async def install(user_id: str, installation_id: int):
    await users.update_one(
        {"_id": user_id},
        {"$set": {"installation_id": installation_id}}
    )
    return {"ok": True}

@router.get("/repos")
async def repos(user_id: str):
    user = await users.find_one({"_id": user_id})
    token = await get_installation_token(user["installation_id"])
    return await get_repos(token)

@router.get("/tree")
async def tree(user_id: str, owner: str, repo: str):
    user = await users.find_one({"_id": user_id})
    token = await get_installation_token(user["installation_id"])
    return await get_tree(token, owner, repo)