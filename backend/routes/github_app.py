from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from db import users_collection
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL")


# 1. Install redirect
@router.get("/github/install")
def install():
    return RedirectResponse(
        "https://github.com/apps/AutodocGen/installations/new"
    )


# 2. Callback after install
@router.get("/github/callback")
def callback(installation_id: int):

    users_collection.update_one(
        {"installation_id": installation_id},
        {"$set": {"installation_id": installation_id}},
        upsert=True
    )

    return RedirectResponse(f"{FRONTEND_URL}/dashboard")