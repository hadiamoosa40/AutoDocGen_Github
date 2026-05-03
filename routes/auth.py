from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from utils.jwt import create_token
from db import save_user, get_user
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@router.get("/auth/github/login")
def github_login():
    """Redirect to GitHub OAuth"""
    if not CLIENT_ID:
        raise HTTPException(500, "GitHub Client ID not configured")
    
    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo,user,read:org"
    print(f"🚀 Redirecting to GitHub OAuth")
    return RedirectResponse(github_url)

@router.get("/auth/github/callback")
def github_callback(code: str):
    """Handle OAuth callback"""
    print(f"📞 Callback received")
    
    # Exchange code for token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        }
    )
    
    token_data = token_response.json()
    
    if "access_token" not in token_data:
        print(f"❌ Failed to get token: {token_data}")
        raise HTTPException(400, "Failed to get access token")
    
    github_token = token_data["access_token"]
    
    # Get user info
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {github_token}"}
    )
    
    user_data = user_response.json()
    
    if "id" not in user_data:
        print(f"❌ Failed to get user: {user_data}")
        raise HTTPException(400, "Failed to get user data")
    
    # Get user's installations
    installations_response = requests.get(
        "https://api.github.com/user/installations",
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json"
        }
    )
    
    installations = installations_response.json()
    installation_id = None
    
    if installations.get("installations"):
        installation_id = installations["installations"][0]["id"]
        print(f"📦 Found installation: {installation_id}")
    
    # Save user
    user_info = {
        "github_id": user_data["id"],
        "username": user_data["login"],
        "name": user_data.get("name", ""),
        "avatar_url": user_data["avatar_url"],
        "github_token": github_token,
        "installation_id": installation_id
    }
    
    save_user(user_data["id"], user_info)
    
    # Create JWT
    jwt_token = create_token({
        "user_id": user_data["id"],
        "username": user_data["login"]
    })
    
    # Redirect to frontend
    redirect_url = f"{FRONTEND_URL}/dashboard?token={jwt_token}"
    print(f"✅ Authentication successful, redirecting")
    
    return RedirectResponse(redirect_url)