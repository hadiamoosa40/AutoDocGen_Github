from fastapi import APIRouter, Depends
from middlewares.auth_middleware import get_current_user
from services.github_api import get_repos, get_repo_contents

router = APIRouter()

@router.get("/repos")
async def repos(user=Depends(get_current_user)):
    return await get_repos(user["github_token"])


@router.get("/repo/{owner}/{repo}")
async def repo(owner: str, repo: str, user=Depends(get_current_user)):
    return await get_repo_contents(user["github_token"], owner, repo)