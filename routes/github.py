from fastapi import APIRouter, HTTPException
from db import users_collection
from services.github_service import get_repos, get_repo

router = APIRouter()


# helper: get current user
def get_current_user():
    return users_collection.find_one({"github_token": {"$exists": True}})


# ✅ GET ALL REPOS (AUTO SHOW AFTER INSTALL)
@router.get("/github/repos")
def repos():

    user = get_current_user()

    if not user:
        raise HTTPException(401, "User not logged in")

    if "installation_id" not in user:
        return {"error": "GitHub App not installed yet"}

    repos = get_repos(user["installation_id"])

    return {
        "repos": repos
    }


# ✅ CLICK REPO → FETCH DATA
@router.get("/github/repo/{owner}/{repo}")
def repo(owner: str, repo: str):

    user = get_current_user()

    if not user:
        raise HTTPException(401, "User not logged in")

    data = get_repo(user["installation_id"], owner, repo)

    # 🔥 YOUR REQUIREMENT: print in backend terminal
    print("🔥 DATA TAKEN FROM REPO:")
    print(data)

    return {
        "message": "data fetched correctly",
        "repo": data
    }