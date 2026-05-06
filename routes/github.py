from fastapi import APIRouter, Depends, HTTPException
from services.github_service import github_service
from middlewares.auth_middleware import JWTBearer
from db import get_users_collection, get_repositories_collection
from typing import List, Dict

router = APIRouter(prefix="/github", tags=["GitHub"])

@router.get("/repos")
async def get_repositories(user: dict = Depends(JWTBearer())):
    """Get user's repositories"""
    # Get user's GitHub token from database
    users_collection = await get_users_collection()
    db_user = await users_collection.find_one({"github_id": user["github_id"]})
    
    if not db_user or "github_token" not in db_user:
        raise HTTPException(401, "GitHub token not found")
    
    # Fetch repositories from GitHub
    repos = await github_service.get_user_repos(db_user["github_token"])
    
    # Save repositories to database
    repos_collection = await get_repositories_collection()
    for repo in repos:
        await repos_collection.update_one(
            {"repo_id": repo["id"]},
            {
                "$set": {
                    "user_id": user["github_id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "html_url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo.get("language"),
                    "updated_at": repo["updated_at"]
                }
            },
            upsert=True
        )
    
    return {
        "repositories": repos,
        "total": len(repos)
    }

@router.get("/repo/{owner}/{repo_name}/contents")
async def get_repo_contents(owner: str, repo_name: str, path: str = "", user: dict = Depends(JWTBearer())):
    """Get repository contents"""
    users_collection = await get_users_collection()
    db_user = await users_collection.find_one({"github_id": user["github_id"]})
    
    if not db_user or "github_token" not in db_user:
        raise HTTPException(401, "GitHub token not found")
    
    contents = await github_service.get_repo_contents(
        db_user["github_token"],
        owner,
        repo_name,
        path
    )
    
    return {"contents": contents}

@router.get("/repo/{owner}/{repo_name}/file")
async def get_file_content(owner: str, repo_name: str, file_path: str, user: dict = Depends(JWTBearer())):
    """Get file content from repository"""
    users_collection = await get_users_collection()
    db_user = await users_collection.find_one({"github_id": user["github_id"]})
    
    if not db_user or "github_token" not in db_user:
        raise HTTPException(401, "GitHub token not found")
    
    content = await github_service.get_file_content(
        db_user["github_token"],
        owner,
        repo_name,
        file_path
    )
    
    if not content:
        raise HTTPException(404, "File not found")
    
    return {"content": content}