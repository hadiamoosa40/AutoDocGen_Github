from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from utils.jwt import create_access_token, create_refresh_token
from db import users_collection
import requests
import os

router = APIRouter()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@router.get("/auth/github/login")
def github_login():
    """Step 1: Redirect to GitHub OAuth page"""
    if not CLIENT_ID:
        raise HTTPException(500, "Missing GITHUB_CLIENT_ID")
    
    github_oauth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&scope=repo,user,read:org"
    )
    
    print(f"🚀 Redirecting to GitHub OAuth: {github_oauth_url}")
    return RedirectResponse(github_oauth_url)

@router.get("/auth/github/callback")
def github_callback(code: str):
    """Step 2: Handle GitHub OAuth callback"""
    print(f"🔥 GitHub callback received with code: {code[:20]}...")
    
    # Exchange code for access token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    )
    
    token_data = token_response.json()
    print(f"📝 Token response received")
    
    if "access_token" not in token_data:
        print(f"❌ Failed to get access token: {token_data}")
        raise HTTPException(400, f"Failed to get access token: {token_data}")
    
    github_token = token_data["access_token"]
    
    # Get user info from GitHub
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {github_token}"}
    )
    
    user_data = user_response.json()
    print(f"👤 GitHub user: {user_data.get('login')} (ID: {user_data.get('id')})")
    
    if "id" not in user_data:
        print(f"❌ Failed to get user data: {user_data}")
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
        print(f"📦 Found installation ID: {installation_id}")
    else:
        print("⚠️ No GitHub App installation found")
    
    # Save user to database
    users_collection.update_one(
        {"github_id": user_data["id"]},
        {
            "$set": {
                "github_id": user_data["id"],
                "username": user_data["login"],
                "name": user_data.get("name", ""),
                "email": user_data.get("email", ""),
                "avatar_url": user_data["avatar_url"],
                "github_token": github_token,
                "installation_id": installation_id,
                "updated_at": requests.get("https://api.github.com/user").elapsed.total_seconds()
            }
        },
        upsert=True
    )
    
    # Create JWT tokens
    access_token = create_access_token({"user_id": user_data["id"], "username": user_data["login"]})
    refresh_token = create_refresh_token({"user_id": user_data["id"]})
    
    print(f"✅ User authenticated successfully. Redirecting to frontend...")
    
    # Redirect to frontend with tokens
    redirect_url = f"{FRONTEND_URL}/dashboard?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)

@router.post("/auth/refresh")
def refresh_token(refresh_token: str):
    """Step 3: Refresh access token"""
    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        
        new_access_token = create_access_token({"user_id": payload["user_id"]})
        return {"access_token": new_access_token}
    except Exception as e:
        raise HTTPException(401, str(e))