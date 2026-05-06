import os
from datetime import datetime, timezone
from bson import ObjectId

from db.database import get_db
from utils.github_utils import create_webhook, delete_webhook
from utils.security import generate_webhook_secret
from utils.ws_manager import ws_manager

BACKEND_URL = os.getenv(
    "BACKEND_URL", "https://autodocgengithub-production.up.railway.app"
)


async def register_webhook(user_id: str, github_token: str, owner: str, repo: str) -> dict:
    db = get_db()
    full_name = f"{owner}/{repo}"

    # Check if webhook already exists for this repo+user
    existing = await db.webhooks.find_one({"user_id": user_id, "repo_full_name": full_name})
    if existing:
        return {
            "message": "Webhook already registered",
            "webhook_id": str(existing["_id"]),
            "github_hook_id": existing.get("github_hook_id"),
        }

    secret = generate_webhook_secret()
    webhook_url = f"{BACKEND_URL}/webhooks/github"

    gh_webhook = await create_webhook(github_token, owner, repo, webhook_url, secret)

    doc = {
        "user_id": user_id,
        "repo_full_name": full_name,
        "owner": owner,
        "repo": repo,
        "github_hook_id": gh_webhook["id"],
        "secret": secret,
        "active": True,
        "created_at": datetime.now(timezone.utc),
        "events": ["push", "pull_request", "create", "delete", "release"],
    }
    result = await db.webhooks.insert_one(doc)

    return {
        "message": "Webhook registered successfully",
        "webhook_id": str(result.inserted_id),
        "github_hook_id": gh_webhook["id"],
    }


async def unregister_webhook(user_id: str, github_token: str, repo_full_name: str):
    db = get_db()
    webhook = await db.webhooks.find_one({"user_id": user_id, "repo_full_name": repo_full_name})
    if not webhook:
        return {"message": "Webhook not found"}

    owner, repo = repo_full_name.split("/", 1)
    await delete_webhook(github_token, owner, repo, webhook["github_hook_id"])
    await db.webhooks.delete_one({"_id": webhook["_id"]})

    return {"message": "Webhook unregistered successfully"}


async def get_user_webhooks(user_id: str) -> list:
    db = get_db()
    cursor = db.webhooks.find({"user_id": user_id})
    webhooks = []
    async for w in cursor:
        w["_id"] = str(w["_id"])
        webhooks.append(w)
    return webhooks


async def handle_webhook_event(repo_full_name: str, event_type: str, payload: dict):
    """Process an incoming GitHub webhook event and broadcast via WebSocket."""
    db = get_db()

    # Store event in DB
    event_doc = {
        "repo_full_name": repo_full_name,
        "event_type": event_type,
        "payload_summary": _summarize_payload(event_type, payload),
        "received_at": datetime.now(timezone.utc),
    }
    await db.webhook_events.insert_one(event_doc)

    # Find which users are subscribed to this repo
    webhooks = db.webhooks.find({"repo_full_name": repo_full_name, "active": True})
    async for webhook in webhooks:
        user_id = webhook["user_id"]
        ws_message = {
            "type": "webhook_event",
            "event": event_type,
            "repo": repo_full_name,
            "summary": event_doc["payload_summary"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await ws_manager.send_to_user(user_id, ws_message)
        print(f"📡 Sent WS event '{event_type}' to user {user_id}")


def _summarize_payload(event_type: str, payload: dict) -> dict:
    """Extract a clean summary from a webhook payload."""
    try:
        if event_type == "push":
            commits = payload.get("commits", [])
            return {
                "ref": payload.get("ref", ""),
                "commits": len(commits),
                "pusher": payload.get("pusher", {}).get("name"),
                "head_commit": commits[0].get("message") if commits else None,
            }
        elif event_type == "pull_request":
            pr = payload.get("pull_request", {})
            return {
                "action": payload.get("action"),
                "pr_number": pr.get("number"),
                "title": pr.get("title"),
                "user": pr.get("user", {}).get("login"),
                "state": pr.get("state"),
            }
        elif event_type in ("create", "delete"):
            return {
                "ref_type": payload.get("ref_type"),
                "ref": payload.get("ref"),
                "sender": payload.get("sender", {}).get("login"),
            }
        elif event_type == "release":
            release = payload.get("release", {})
            return {
                "action": payload.get("action"),
                "tag": release.get("tag_name"),
                "name": release.get("name"),
                "author": release.get("author", {}).get("login"),
            }
    except Exception:
        pass
    return {"raw": str(payload)[:200]}