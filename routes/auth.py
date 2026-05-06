from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import httpx

from config import *
from db import users
from utils.jwt import create_token

router = APIRouter()

# STEP 1: Login
@router.get("/login")
async def login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    )

# STEP 2: OAuth callback
@router.get("/callback")
async def callback(code: str):

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            }
        )

        access_token = token_res.json()["access_token"]

        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        gh_user = user_res.json()

    user = await users.find_one({"github_id": gh_user["id"]})

    if not user:
        result = await users.insert_one({
            "github_id": gh_user["id"],
            "username": gh_user["login"],
            "installation_id": None
        })
        user = await users.find_one({"_id": result.inserted_id})

    jwt_token = create_token(str(user["_id"]))

    return RedirectResponse(
        f"{FRONTEND_URL}/dashboard?token={jwt_token}&uid={user['_id']}"
    )