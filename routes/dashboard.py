from fastapi import APIRouter, Depends, HTTPException
from db import users_collection
from services.github_service import get_user_repos
from middlewares.auth_middleware import get_current_user

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get dashboard data for authenticated user"""
    
    user_id = current_user.get("user_id")
    print(f"📊 Dashboard requested for user ID: {user_id}")
    
    # Find user in database
    db_user = users_collection.find_one({"github_id": user_id})
    
    if not db_user:
        print(f"❌ User {user_id} not found in database")
        raise HTTPException(404, "User not found")
    
    # Check if GitHub App is installed
    installation_id = db_user.get("installation_id")
    
    if not installation_id:
        print(f"⚠️ GitHub App not installed for user {db_user.get('username')}")
        return {
            "authenticated": True,
            "user": {
                "username": db_user.get("username"),
                "avatar_url": db_user.get("avatar_url")
            },
            "github_app_installed": False,
            "repositories": []
        }
    
    # Get repositories
    print(f"📚 Fetching repositories for user {db_user.get('username')}")
    repositories = get_user_repos(installation_id)
    
    return {
        "authenticated": True,
        "user": {
            "username": db_user.get("username"),
            "avatar_url": db_user.get("avatar_url")
        },
        "github_app_installed": True,
        "repositories": repositories
    }