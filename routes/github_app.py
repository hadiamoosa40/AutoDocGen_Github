from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from db import users_collection
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.get("/github/install")
def install():
    return RedirectResponse(
        "https://github.com/apps/AutodocGen/installations/new"
    )


# 🔥 AFTER INSTALL REDIRECT (IMPROVED)
@router.get("/github/callback")
def callback(installation_id: int = None, setup_action: str = None):

    user = users_collection.find_one({"github_token": {"$exists": True}})

    if installation_id and user:
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"installation_id": installation_id}}
        )

    # 🔥 IMPORTANT: redirect with flag
    return RedirectResponse(
        f"{FRONTEND_URL}/dashboard?installed=true"
    )