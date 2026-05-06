import hmac
import hashlib
import os

from fastapi import APIRouter, Request, HTTPException, Header, status
from pydantic import BaseModel

from services.webhook_service import (
    register_webhook,
    unregister_webhook,
    get_user_webhooks,
    handle_webhook_event,
)
from services.auth_service import get_user_by_id
from db.database import get_db

router = APIRouter()

GITHUB_WEBHOOK_SECRET_GLOBAL = os.getenv("GITHUB_WEBHOOK_SECRET", "")


async def _get_github_token(request: Request) -> str:
    user_id = request.state.user_id
    user = await get_user_by_id(user_id)
    return user["github_token"]


class WebhookRegisterRequest(BaseModel):
    owner: str
    repo: str


class WebhookDeleteRequest(BaseModel):
    repo_full_name: str


@router.post("/register")
async def register(body: WebhookRegisterRequest, request: Request):
    """Register a GitHub webhook for a repo."""
    user_id = request.state.user_id
    github_token = await _get_github_token(request)
    result = await register_webhook(user_id, github_token, body.owner, body.repo)
    return result


@router.delete("/unregister")
async def unregister(body: WebhookDeleteRequest, request: Request):
    """Remove a GitHub webhook for a repo."""
    user_id = request.state.user_id
    github_token = await _get_github_token(request)
    result = await unregister_webhook(user_id, github_token, body.repo_full_name)
    return result


@router.get("/")
async def list_webhooks(request: Request):
    """List all registered webhooks for the current user."""
    user_id = request.state.user_id
    webhooks = await get_user_webhooks(user_id)
    return {"webhooks": webhooks}


@router.post("/github")
async def receive_github_webhook(
    request: Request,
    x_github_event: str = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
):
    """Receive and process GitHub webhook events."""
    payload_body = await request.body()

    # Verify signature using per-repo secret stored in DB
    repo_full_name = None
    try:
        import json
        data = json.loads(payload_body)
        repo = data.get("repository", {})
        repo_full_name = repo.get("full_name")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Find webhook record to get the per-repo secret
    db = get_db()
    webhook_doc = await db.webhooks.find_one({"repo_full_name": repo_full_name})

    if webhook_doc:
        secret = webhook_doc.get("secret", "").encode("utf-8")
        if x_hub_signature_256:
            expected = "sha256=" + hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, x_hub_signature_256):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid webhook signature",
                )

    # Process event
    event_type = x_github_event or "unknown"
    await handle_webhook_event(repo_full_name, event_type, data)

    return {"status": "received", "event": event_type, "repo": repo_full_name}