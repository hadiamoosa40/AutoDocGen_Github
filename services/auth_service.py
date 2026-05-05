import requests
import os
from db import users_collection

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")


def exchange_code_for_token(code: str):
    res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    )
    return res.json().get("access_token")


def get_github_user(token: str):
    res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token}"}
    )
    return res.json()


def save_user(user, token):
    return users_collection.update_one(
        {"github_id": user["id"]},
        {
            "$set": {
                "github_id": user["id"],
                "username": user["login"],
                "avatar": user["avatar_url"],
                "github_token": token
            }
        },
        upsert=True
    )