from fastapi import APIRouter
from db import users_collection
from services.github_service import get_repos, get_repo

router = APIRouter()


def get_user():
    return users_collection.find_one({})


@router.get("/github/repos")
def repos():

    user = get_user()
    return get_repos(user["installation_id"])


@router.get("/github/repo/{owner}/{repo}")
def repo(owner: str, repo: str):

    user = get_user()

    return {
        "message": "data fetched correctly",
        "repo": get_repo(user["installation_id"], owner, repo)
    }