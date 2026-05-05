import os
from fastapi import APIRouter, Depends
from db import users_collection
from middlewares.auth_middleware import get_current_user

router = APIRouter()

APP_NAME = os.getenv("GITHUB_APP_NAME")


@router.get("/github-app/install")
def install():
    return {
        "url": f"https://github.com/apps/{APP_NAME}/installations/new"
    }


@router.get("/github-app/callback")
def callback(installation_id: int, user=Depends(get_current_user)):

    users_collection.update_one(
        {"github_id": user["github_id"]},
        {"$set": {"installation_id": installation_id}},
        upsert=True
    )

    return {"success": True}