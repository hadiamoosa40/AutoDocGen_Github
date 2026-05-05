from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from db import users_collection
from middlewares.auth_middleware import get_current_user
from fastapi import Depends
import os

router = APIRouter()

GITHUB_APP_NAME = os.getenv("GITHUB_APP_NAME", "AutodocGen")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@router.get("/github-app/install")
def install_github_app():
    """Redirect to GitHub App installation page"""
    install_url = f"https://github.com/apps/{GITHUB_APP_NAME}/installations/new"
    return RedirectResponse(install_url)

@router.get("/github-app/callback")
def github_app_callback(installation_id: int = None, setup_action: str = None, current_user: dict = Depends(get_current_user)):
    """Handle GitHub App installation callback"""
    
    if not installation_id:
        raise HTTPException(400, "No installation ID provided")
    
    user_id = current_user.get("user_id")
    
    # Update user with installation ID
    result = users_collection.update_one(
        {"github_id": user_id},
        {"$set": {"installation_id": installation_id}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Installation ID {installation_id} saved for user {user_id}")
    else:
        print(f"⚠️ Failed to save installation ID for user {user_id}")
    
    # Redirect to dashboard
    return RedirectResponse(f"{FRONTEND_URL}/dashboard?installed=true")