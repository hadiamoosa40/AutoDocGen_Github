from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from services.github_service import exchange_code, get_user
from services.encryption_service import encrypt
from utils.jwt_handler import create_access_token, create_refresh_token
from db import users
from config import *

router = APIRouter()

@router.get("/login")
async def login():
    return RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}")

@router.get("/callback")
async def callback(code: str):
    data = await exchange_code(code, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    token = data["access_token"]

    gh_user = await get_user(token)
    enc = encrypt(token)

    user = await users.find_one({"github_id": gh_user["id"]})

    if not user:
        result = await users.insert_one({
            "github_id": gh_user["id"],
            "username": gh_user["login"],
            "token": enc
        })
        user = await users.find_one({"_id": result.inserted_id})

    access = create_access_token({"id": str(user["_id"])})
    refresh = create_refresh_token({"id": str(user["_id"])})

    return RedirectResponse(f"{FRONTEND_URL}/dashboard?access={access}&uid={user['_id']}")