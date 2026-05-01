from fastapi import APIRouter, Depends
from db import users_collection
from services.github_service import get_repos
from middlewares.auth_middleware import get_current_user

router = APIRouter()

@router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):

    db_user = users_collection.find_one({"github_id": user["user_id"]})

    if not db_user:
        return {"logged_in": False}

    if "installation_id" not in db_user:
        return {
            "installed": False,
            "repos": []
        }

    repos = get_repos(db_user["installation_id"])

    return {
        "installed": True,
        "repos": repos
    }