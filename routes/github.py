from fastapi import APIRouter, Depends, HTTPException
from db import users_collection
from services.github_service import get_user_repos, get_repo_data, get_repo_contents
from middlewares.auth_middleware import get_current_user

router = APIRouter()

@router.get("/github/installations")
def check_installation(current_user: dict = Depends(get_current_user)):
    """Check if GitHub App is installed"""
    user_id = current_user.get("user_id")
    db_user = users_collection.find_one({"github_id": user_id})
    
    if not db_user:
        raise HTTPException(404, "User not found")
    
    return {
        "installed": bool(db_user.get("installation_id")),
        "installation_id": db_user.get("installation_id")
    }

@router.get("/github/repositories")
def get_repositories(current_user: dict = Depends(get_current_user)):
    """Get all repositories for the user"""
    user_id = current_user.get("user_id")
    db_user = users_collection.find_one({"github_id": user_id})
    
    if not db_user:
        raise HTTPException(404, "User not found")
    
    installation_id = db_user.get("installation_id")
    
    if not installation_id:
        return {
            "installed": False,
            "repositories": [],
            "message": "GitHub App not installed. Please install the app first."
        }
    
    repositories = get_user_repos(installation_id)
    
    return {
        "installed": True,
        "repositories": repositories
    }

@router.get("/github/repository/{owner}/{repo_name}")
def get_repository(owner: str, repo_name: str, current_user: dict = Depends(get_current_user)):
    """Get detailed data for a specific repository"""
    user_id = current_user.get("user_id")
    db_user = users_collection.find_one({"github_id": user_id})
    
    if not db_user:
        raise HTTPException(404, "User not found")
    
    installation_id = db_user.get("installation_id")
    
    if not installation_id:
        raise HTTPException(400, "GitHub App not installed")
    
    print(f"\n🚀 Fetching data for repository: {owner}/{repo_name}")
    
    repo_data = get_repo_data(installation_id, owner, repo_name)
    
    if not repo_data:
        raise HTTPException(404, f"Repository {owner}/{repo_name} not found")
    
    return {
        "success": True,
        "message": f"Data fetched successfully for {owner}/{repo_name}",
        "data": repo_data
    }

@router.get("/github/repository/{owner}/{repo_name}/contents")
def get_repository_contents(owner: str, repo_name: str, path: str = "", current_user: dict = Depends(get_current_user)):
    """Get contents of a repository"""
    user_id = current_user.get("user_id")
    db_user = users_collection.find_one({"github_id": user_id})
    
    if not db_user:
        raise HTTPException(404, "User not found")
    
    installation_id = db_user.get("installation_id")
    
    if not installation_id:
        raise HTTPException(400, "GitHub App not installed")
    
    contents = get_repo_contents(installation_id, owner, repo_name, path)
    
    return {
        "success": True,
        "path": path,
        "contents": contents
    }