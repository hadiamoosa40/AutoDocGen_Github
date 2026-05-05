from fastapi import APIRouter, Depends
from middlewares.auth_middleware import get_current_user
from db import users_collection
from services.github_service import (
    get_user_repos,
    get_repo_code
)

router = APIRouter()


@router.get("/repos")
def repos(user=Depends(get_current_user)):

    db_user = users_collection.find_one(
        {"github_id": user["github_id"]}
    )

    return get_user_repos(db_user["github_token"])


@router.get("/repo/{owner}/{repo}")
def repo(owner: str, repo: str, user=Depends(get_current_user)):

    db_user = users_collection.find_one(
        {"github_id": user["github_id"]}
    )

    files = get_repo_code(
        db_user["github_token"],
        owner,
        repo
    )

    return {
        "repo": f"{owner}/{repo}",
        "files": files
    }from fastapi import APIRouter, Depends
from middlewares.auth_middleware import get_current_user
from db import users_collection
from services.github_service import (
    get_user_repos,
    get_repo_code
)

router = APIRouter()


@router.get("/repos")
def repos(user=Depends(get_current_user)):

    db_user = users_collection.find_one(
        {"github_id": user["github_id"]}
    )

    return get_user_repos(db_user["github_token"])


@router.get("/repo/{owner}/{repo}")
def repo(owner: str, repo: str, user=Depends(get_current_user)):

    db_user = users_collection.find_one(
        {"github_id": user["github_id"]}
    )

    files = get_repo_code(
        db_user["github_token"],
        owner,
        repo
    )

    return {
        "repo": f"{owner}/{repo}",
        "files": files
    }