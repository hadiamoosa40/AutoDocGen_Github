from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from app.utils.github_client import github_client
from app.services.auth_service import AuthService
from app.db import get_collection
import os
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@router.get("/github/login")
async def github_login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=repo,user"
    return {"auth_url": github_auth_url}

@router.get("/github/callback")
async def github_callback(code: str = Query(...)):
    # Exchange code for access token
    access_token = await github_client.get_access_token(
        code, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI
    )
    
    # Get user info from GitHub
    github_user = await github_client.get_user_info(access_token)
    
    # Create or update user in database
    user = await AuthService.create_or_update_user(github_user, access_token)
    
    # Generate JWT
    jwt_token = AuthService.generate_jwt(user)
    
    # Store token in database for later use
    collection = get_collection("users")
    await collection.update_one(
        {"github_id": user.github_id},
        {"$set": {"jwt_token": jwt_token}}
    )
    
    # Redirect to frontend with token
    redirect_url = f"{FRONTEND_URL}/auth/callback?token={jwt_token}&username={user.username}"
    return RedirectResponse(url=redirect_url)

@router.get("/me")
async def get_current_user(request: Request):
    from app.middlewares.auth_middleware import get_current_user
    user = await get_current_user(request)
    return {
        "id": user.github_id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "email": user.email
    }

@router.post("/logout")
async def logout(request: Request):
    # In a real implementation, you might want to blacklist the token
    return {"message": "Logged out successfully"}