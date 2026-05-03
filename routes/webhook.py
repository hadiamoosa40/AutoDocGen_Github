from fastapi import APIRouter, Request, HTTPException
import os
import hashlib
import hmac

router = APIRouter()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    
    # Get event type
    event_type = request.headers.get("X-GitHub-Event")
    
    # Verify signature (optional)
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Read body
    body = await request.body()
    
    # Parse payload
    try:
        payload = await request.json()
    except:
        payload = {}
    
    print(f"\n{'='*60}")
    print(f"🔥 WEBHOOK RECEIVED")
    print(f"📌 Event: {event_type}")
    print(f"{'='*60}\n")
    
    if event_type == "installation":
        action = payload.get("action")
        installation_id = payload.get("installation", {}).get("id")
        
        print(f"📦 Installation Event - Action: {action}")
        print(f"   Installation ID: {installation_id}")
        
        if action == "created":
            print(f"✅ New GitHub App installation created")
        elif action == "deleted":
            print(f"❌ GitHub App uninstalled")
    
    elif event_type == "push":
        repository = payload.get("repository", {}).get("full_name")
        pusher = payload.get("pusher", {}).get("name")
        commits = len(payload.get("commits", []))
        
        print(f"📝 Push Event:")
        print(f"   • Repository: {repository}")
        print(f"   • Pusher: {pusher}")
        print(f"   • Commits: {commits}")
        
        for commit in payload.get("commits", [])[:3]:  # Show first 3 commits
            print(f"     - {commit.get('message').split(chr(10))[0][:50]}")
    
    elif event_type == "repository":
        action = payload.get("action")
        repository = payload.get("repository", {}).get("full_name")
        
        print(f"📚 Repository Event - Action: {action}")
        print(f"   Repository: {repository}")
    
    else:
        print(f"📨 Received event: {event_type}")
    
    return {"status": "received", "event": event_type}