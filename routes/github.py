from fastapi import APIRouter
from db import users
from services.encryption_service import decrypt
from services.github_service import get_repos, get_tree

router = APIRouter()

@router.get("/repos")
async def repos(uid: str):
    user = await users.find_one({"_id": uid})
    token = decrypt(user["token"])
    return await get_repos(token)

@router.get("/tree")
async def tree(uid: str, owner: str, repo: str):
    user = await users.find_one({"_id": uid})
    token = decrypt(user["token"])
    return await get_tree(token, owner, repo)