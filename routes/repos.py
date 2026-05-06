from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional, Dict, Any
from app.services.repo_service import RepoService
from app.services.doc_generator import doc_generator
from app.middlewares.auth_middleware import get_current_user
from app.db import get_collection
from app.models.user import User

router = APIRouter(prefix="/repos", tags=["repositories"])

@router.get("/list")
async def get_user_repos(request: Request, user: User = Depends(get_current_user)):
    # Get stored access token
    collection = get_collection("users")
    user_data = await collection.find_one({"github_id": user.github_id})
    
    if not user_data or "access_token" not in user_data:
        raise HTTPException(status_code=401, detail="GitHub access token not found")
    
    repos = await RepoService.get_repos(
        user_data["access_token"],
        str(user.github_id)
    )
    
    return {
        "repos": [{"name": repo["full_name"], "id": repo["id"], "description": repo.get("description")} for repo in repos]
    }

@router.get("/{repo_full_name:path}/contents")
async def get_repo_contents(
    repo_full_name: str,
    path: str = "",
    request: Request = None,
    user: User = Depends(get_current_user)
):
    collection = get_collection("users")
    user_data = await collection.find_one({"github_id": user.github_id})
    
    if not user_data or "access_token" not in user_data:
        raise HTTPException(status_code=401, detail="GitHub access token not found")
    
    contents = await RepoService.get_repo_tree(
        user_data["access_token"],
        repo_full_name,
        str(user.github_id),
        path
    )
    
    return {"contents": contents}

@router.post("/{repo_full_name:path}/generate-docs")
async def generate_repo_docs(
    repo_full_name: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    collection = get_collection("users")
    user_data = await collection.find_one({"github_id": user.github_id})
    
    if not user_data or "access_token" not in user_data:
        raise HTTPException(status_code=401, detail="GitHub access token not found")
    
    # Fetch all code files
    files = await RepoService.fetch_all_code(
        user_data["access_token"],
        repo_full_name,
        str(user.github_id)
    )
    
    # Generate documentation
    documentation = await doc_generator.generate_documentation(
        files,
        repo_full_name,
        str(user.github_id)
    )
    
    # Store documentation in database
    docs_collection = get_collection("documentations")
    await docs_collection.update_one(
        {"repo_name": repo_full_name, "user_id": user.github_id},
        {"$set": {
            "documentation": documentation,
            "files_count": len(files),
            "generated_at": "datetime.utcnow()"
        }},
        upsert=True
    )
    
    return {
        "message": "Documentation generated successfully",
        "repo": repo_full_name,
        "files_processed": len(files),
        "documentation": documentation[:1000] + "..."  # Preview
    }