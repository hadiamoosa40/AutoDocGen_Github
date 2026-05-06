from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId

from db.database import get_db
from utils.jwt_utils import create_access_token, create_refresh_token, verify_refresh_token
from utils.github_utils import get_github_user, get_github_user_emails
from fastapi import HTTPException, status


async def upsert_github_user(github_token: str) -> dict:
    """Fetch GitHub user and upsert into MongoDB. Returns user dict."""
    db = get_db()

    # Fetch user + emails from GitHub
    gh_user = await get_github_user(github_token)
    emails = await get_github_user_emails(github_token)

    # Determine primary email
    primary_email = gh_user.get("email")
    if not primary_email and emails:
        for e in emails:
            if e.get("primary") and e.get("verified"):
                primary_email = e["email"]
                break
        if not primary_email and emails:
            primary_email = emails[0]["email"]

    now = datetime.now(timezone.utc)
    user_data = {
        "github_id": gh_user["id"],
        "username": gh_user["login"],
        "name": gh_user.get("name"),
        "email": primary_email,
        "avatar_url": gh_user.get("avatar_url"),
        "bio": gh_user.get("bio"),
        "public_repos": gh_user.get("public_repos", 0),
        "followers": gh_user.get("followers", 0),
        "following": gh_user.get("following", 0),
        "github_token": github_token,  # Encrypted in prod; store encrypted
        "updated_at": now,
    }

    result = await db.users.find_one_and_update(
        {"github_id": gh_user["id"]},
        {
            "$set": user_data,
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=True,
    )

    if result is None:
        result = await db.users.find_one({"github_id": gh_user["id"]})

    return result


async def create_token_pair(user: dict) -> dict:
    """Create access + refresh token pair and store refresh token."""
    db = get_db()
    user_id = str(user["_id"])

    token_data = {"sub": user_id, "username": user["username"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token in DB (for revocation support)
    from utils.jwt_utils import decode_token
    rt_payload = decode_token(refresh_token)
    await db.tokens.insert_one({
        "user_id": user_id,
        "jti": rt_payload["jti"],
        "type": "refresh",
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.fromtimestamp(rt_payload["exp"], tz=timezone.utc),
        "revoked": False,
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }


async def refresh_access_token(refresh_token: str) -> dict:
    """Validate refresh token and issue new access token."""
    db = get_db()
    payload = verify_refresh_token(refresh_token)

    # Check if token is revoked
    token_doc = await db.tokens.find_one({"jti": payload["jti"]})
    if not token_doc or token_doc.get("revoked"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return await create_token_pair(user)


async def revoke_refresh_token(jti: str):
    """Revoke a specific refresh token."""
    db = get_db()
    await db.tokens.update_one({"jti": jti}, {"$set": {"revoked": True}})


async def get_user_by_id(user_id: str) -> Optional[dict]:
    db = get_db()
    try:
        return await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None