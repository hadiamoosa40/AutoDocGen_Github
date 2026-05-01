from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from db import users_collection
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL")


# Step 1: install GitHub App
@router.get("/github/install")
def install():
    return RedirectResponse(
        "https://github.com/apps/AutodocGen/installations/new"
    )


# Step 2: GitHub redirects after install
@router.get("/github/callback")
def callback(installation_id: int = None, setup_action: str = None):

    # 🔥 FIX: always attach installation to latest logged-in user
    user = users_collection.find_one({"github_token": {"$exists": True}})

    if not user:
        return {"error": "User not logged in"}

    if installation_id:
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"installation_id": installation_id}}
        )

    return RedirectResponse(f"{FRONTEND_URL}/dashboard")