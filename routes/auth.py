from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import httpx
from config import *
from db import users
from services.jwt_service import create_token

router = APIRouter()

@router.get("/login")
async def login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    )

@router.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            }
        )
        token = res.json()["access_token"]

        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"}
        )

        gh_user = user_res.json()

        db_user = await users.find_one({"github_id": gh_user["id"]})

        if not db_user:
            result = await users.insert_one({
                "github_id": gh_user["id"],
                "username": gh_user["login"],
                "installation_id": None
            })
            db_user = await users.find_one({"_id": result.inserted_id})

        jwt_token = create_token({"id": str(db_user["_id"])})

        return RedirectResponse(f"{FRONTEND_URL}/dashboard?token={jwt_token}&uid={db_user['_id']}")