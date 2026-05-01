from dotenv import load_dotenv

load_dotenv()
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from utils.jwt import create_access_token, create_refresh_token
from db import users_collection
from datetime import datetime
import requests
import os


router = APIRouter()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.get("/auth/github/login")
def login():
    if not CLIENT_ID:
        raise HTTPException(500, "Missing GITHUB_CLIENT_ID")

    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=repo,user"
    )

    return RedirectResponse(url)


from datetime import datetime

@router.get("/auth/github/callback")
def github_callback(code: str):

    print("🔥 CALLBACK HIT")

    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    )

    token_json = token_res.json()
    print("TOKEN RESPONSE:", token_json)

    if "access_token" not in token_json:
        print("❌ TOKEN FAILED")
        return {"error": token_json}

    github_token = token_json["access_token"]

    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {github_token}"},
    )

    user = user_res.json()
    print("USER:", user)

    if "id" not in user:
        print("❌ USER FETCH FAILED")
        return {"error": user}

    # Get user's installations
    installations_res = requests.get(
        "https://api.github.com/user/installations",
        headers={"Authorization": f"token {github_token}"},
    )
    installations = installations_res.json()
    
    installation_id = None
    if installations.get("installations"):
        installation_id = installations["installations"][0]["id"]
    
    # Store both token AND installation_id
    users_collection.update_one(
        {"github_id": user["id"]},
        {
            "$set": {
                "github_id": user["id"],
                "username": user["login"],
                "avatar": user["avatar_url"],
                "github_token": github_token,
                "installation_id": installation_id  # ADD THIS
            }
        },
        upsert=True
    )
    

    access = create_access_token({"user_id": user["id"]})
    refresh = create_refresh_token({"user_id": user["id"]})

    print("✅ SUCCESS REDIRECTING")

    return RedirectResponse(
    f"{FRONTEND_URL}/dashboard?access={access}&refresh={refresh}"
)