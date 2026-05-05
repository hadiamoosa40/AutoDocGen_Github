from fastapi import APIRouter
from services.github_oauth import exchange_code, get_user
from utils.jwt import create_token
from db import users

router = APIRouter()

@router.get("/auth/github/callback")
async def github_callback(code: str):
    gh_token = await exchange_code(code)
    user = await get_user(gh_token)

    await users.update_one(
        {"github_id": user["id"]},
        {"$set": {"login": user["login"], "token": gh_token}},
        upsert=True,
    )

    jwt_token = create_token({
        "github_id": user["id"],
        "github_token": gh_token
    })

    return {"token": jwt_token}