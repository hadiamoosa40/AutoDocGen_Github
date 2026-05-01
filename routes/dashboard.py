from fastapi import APIRouter
from db import users_collection
from services.github_service import get_repos

router = APIRouter()

@router.get("/dashboard")
def dashboard():

    user = users_collection.find_one({"github_token": {"$exists": True}})

    if not user:
        return {"logged_in": False}

    if "installation_id" not in user:
        return {
            "logged_in": True,
            "installed": False,
            "repos": []
        }

    repos = get_repos(user["installation_id"])

    return {
        "logged_in": True,
        "installed": True,
        "repos": repos
    }