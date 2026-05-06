from fastapi import APIRouter, HTTPException, Request, Header
from app.utils.websocket_manager import manager
import hmac
import hashlib
import os
from typing import Optional

router = APIRouter(prefix="/webhook", tags=["webhooks"])
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_webhook_secret_here")

def verify_signature(payload: bytes, signature: str) -> bool:
    if not signature:
        return False
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    # Get raw body
    body = await request.body()
    
    # Verify signature
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    payload = await request.json()
    
    # Handle different event types
    event_handlers = {
        "push": handle_push_event,
        "pull_request": handle_pr_event,
        "star": handle_star_event
    }
    
    handler = event_handlers.get(x_github_event)
    if handler:
        await handler(payload)
    
    return {"status": "received"}

async def handle_push_event(payload: dict):
    # Extract relevant info
    repo_name = payload.get("repository", {}).get("full_name")
    pusher = payload.get("pusher", {}).get("name")
    commits = payload.get("commits", [])
    
    # Broadcast to connected clients
    await manager.broadcast({
        "type": "push_event",
        "repo": repo_name,
        "pusher": pusher,
        "commits_count": len(commits),
        "message": f"New push to {repo_name} by {pusher}"
    })

async def handle_pr_event(payload: dict):
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo_name = payload.get("repository", {}).get("full_name")
    
    await manager.broadcast({
        "type": "pr_event",
        "action": action,
        "repo": repo_name,
        "title": pr.get("title"),
        "url": pr.get("html_url")
    })

async def handle_star_event(payload: dict):
    action = payload.get("action")
    repo_name = payload.get("repository", {}).get("full_name")
    sender = payload.get("sender", {}).get("login")
    
    await manager.broadcast({
        "type": "star_event",
        "action": action,
        "repo": repo_name,
        "user": sender
    })