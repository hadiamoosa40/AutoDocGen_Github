from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.github_service import github_service
from services.token_service import token_service
from utils.jwt_utils import create_access_token, create_refresh_token
from db import get_users_collection
from datetime import datetime
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.get("/github/login")
async def github_login():
    """Redirect to GitHub OAuth page"""
    client_id = os.getenv("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(500, "GitHub Client ID not configured")
    
    github_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo,user,read:org"
    print(f"🚀 Redirecting to GitHub OAuth")
    return RedirectResponse(github_url)

@router.get("/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback"""
    try:
        print(f"📞 Callback received with code: {code[:20]}...")
        
        # Exchange code for access token
        access_token = await github_service.exchange_code_for_token(code)
        if not access_token:
            raise HTTPException(400, "Failed to get access token")
        
        # Get GitHub user
        user_data = await github_service.get_github_user(access_token)
        if not user_data:
            raise HTTPException(400, "Failed to get user data")
        
        print(f"👤 User authenticated: {user_data['login']} (ID: {user_data['id']})")
        
        # Save or update user
        users_collection = await get_users_collection()
        if users_collection:
            await users_collection.update_one(
                {"github_id": user_data["id"]},
                {
                    "$set": {
                        "username": user_data["login"],
                        "email": user_data.get("email"),
                        "avatar_url": user_data["avatar_url"],
                        "name": user_data.get("name"),
                        "github_token": access_token,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        # Create JWT tokens
        jwt_access_token = create_access_token({
            "user_id": user_data["id"],
            "username": user_data["login"]
        })
        jwt_refresh_token = create_refresh_token({
            "user_id": user_data["id"],
            "username": user_data["login"]
        })
        
        # Save tokens
        await token_service.save_user_token(user_data["id"], jwt_access_token, jwt_refresh_token)
        
        # Redirect to frontend
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/dashboard?token={jwt_access_token}&refresh={jwt_refresh_token}"
        print(f"✅ Authentication successful, redirecting to dashboard")
        
        return RedirectResponse(redirect_url)
    
    except Exception as e:
        print(f"❌ Error in callback: {str(e)}")
        raise HTTPException(500, f"Authentication error: {str(e)}")

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    new_tokens = await token_service.refresh_access_token(refresh_token)
    if not new_tokens:
        raise HTTPException(401, "Invalid refresh token")
    return new_tokens

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    user = await token_service.get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    
    # Convert ObjectId to string if it exists
    if user.get("_id"):
        user["_id"] = str(user["_id"])
    return user