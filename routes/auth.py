from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@router.get("/auth/github/login")
def github_login():
    """Redirect to GitHub OAuth"""
    print("🔐 Login endpoint called")
    
    if not CLIENT_ID:
        print("❌ CLIENT_ID missing")
        raise HTTPException(500, "GitHub Client ID not configured")
    
    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo,user,read:org"
    print(f"🚀 Redirecting to GitHub OAuth")
    return RedirectResponse(github_url)

@router.get("/auth/github/callback")
def github_callback(code: str):
    """Handle OAuth callback"""
    print(f"📞 Callback received with code: {code[:20]}...")
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ GitHub credentials missing")
        raise HTTPException(500, "GitHub credentials not configured")
    
    # Exchange code for token
    try:
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
            },
            timeout=10
        )
        
        token_data = token_response.json()
        print(f"📝 Token response received")
        
        if "access_token" not in token_data:
            print(f"❌ Failed to get token: {token_data}")
            raise HTTPException(400, "Failed to get access token")
        
        github_token = token_data["access_token"]
        
        # Get user info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_token}"},
            timeout=10
        )
        
        user_data = user_response.json()
        
        if "id" not in user_data:
            print(f"❌ Failed to get user: {user_data}")
            raise HTTPException(400, "Failed to get user data")
        
        username = user_data.get("login")
        user_id = user_data["id"]
        
        print(f"👤 User authenticated: {username} (ID: {user_id})")
        
        # Create a simple token (since JWT might have issues)
        simple_token = f"{user_id}_{username}_{github_token[:50]}"
        
        # Redirect to frontend
        redirect_url = f"{FRONTEND_URL}/dashboard?token={simple_token}&username={username}"
        print(f"✅ Authentication successful, redirecting to: {redirect_url}")
        
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        print(f"❌ Error in callback: {str(e)}")
        raise HTTPException(500, f"Authentication error: {str(e)}")