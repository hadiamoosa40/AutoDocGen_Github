from fastapi import APIRouter, Request, HTTPException
from db import users_collection
import hashlib
import hmac
import os

router = APIRouter()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def verify_webhook_signature(request: Request, payload: bytes, signature: str):
    """Verify webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret set
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    
    # Get event type
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Read body
    body = await request.body()
    
    # Verify signature (optional)
    if signature and not verify_webhook_signature(request, body, signature):
        raise HTTPException(401, "Invalid signature")
    
    # Parse payload
    try:
        payload = await request.json()
    except:
        payload = {}
    
    print(f"\n{'='*60}")
    print(f"🔥 WEBHOOK RECEIVED")
    print(f"📌 Event: {event_type}")
    print(f"{'='*60}\n")
    
    # Handle different event types
    if event_type == "installation":
        action = payload.get("action")
        installation_id = payload.get("installation", {}).get("id")
        
        print(f"📦 Installation Event - Action: {action}, ID: {installation_id}")
        
        if action == "created":
            # New installation - we can't directly link to user here
            print(f"✅ New GitHub App installation: {installation_id}")
            
    elif event_type == "push":
        repository = payload.get("repository", {}).get("full_name")
        pusher = payload.get("pusher", {}).get("name")
        commits = len(payload.get("commits", []))
        
        print(f"📝 Push Event:")
        print(f"  • Repository: {repository}")
        print(f"  • Pusher: {pusher}")
        print(f"  • Commits: {commits}")
        
    elif event_type == "repository":
        action = payload.get("action")
        repository = payload.get("repository", {}).get("full_name")
        
        print(f"📚 Repository Event - Action: {action}, Repo: {repository}")
    
    return {"status": "received", "event": event_type}