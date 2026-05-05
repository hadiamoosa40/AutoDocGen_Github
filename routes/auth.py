from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services.auth_service import (
    exchange_code_for_token,
    get_github_user,
    save_user
)
from utils.jwt import create_token
import os

router = APIRouter()

FRONTEND = os.getenv("FRONTEND_URL")


@router.get("/auth/github/login")
def login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={os.getenv('GITHUB_CLIENT_ID')}&scope=repo"
    )


@router.get("/auth/github/callback")
def callback(code: str):

    token = exchange_code_for_token(code)

    if not token:
        raise HTTPException(400, "OAuth failed")

    user = get_github_user(token)

    save_user(user, token)

    jwt_token = create_token({
        "github_id": user["id"],
        "username": user["login"]
    })

    return RedirectResponse(
        f"{FRONTEND}/dashboard?token={jwt_token}"
    )