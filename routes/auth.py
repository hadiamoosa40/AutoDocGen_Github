from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services.github_oauth import exchange_code, get_user
from utils.jwt import create_token
from db import users
from config import FRONTEND_URL

router = APIRouter()

@router.get("/auth/github/callback")
async def github_callback(code: str):
    gh_token = await exchange_code(code)

    if not gh_token:
        raise HTTPException(status_code=400, detail="Failed to get GitHub token")

    user = await get_user(gh_token)

    if "id" not in user:
        raise HTTPException(status_code=400, detail=f"GitHub error: {user}")

    await users.update_one(
        {"github_id": user["id"]},
        {"$set": {"login": user["login"], "token": gh_token}},
        upsert=True,
    )

    jwt_token = create_token({
        "github_id": user["id"],
        "github_token": gh_token
    })

    # 🔥 REDIRECT TO FRONTEND (CORRECT FLOW)
    return RedirectResponse(
        url=f"{FRONTEND_URL}/callback?token={jwt_token}"
    )