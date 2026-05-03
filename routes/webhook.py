from fastapi import APIRouter, Request
import os

router = APIRouter()

@router.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    
    # Get event type
    event_type = request.headers.get("X-GitHub-Event")
    
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
    
    elif event_type == "push":
        repository = payload.get("repository", {}).get("full_name")
        commits = len(payload.get("commits", []))
        print(f"📝 Push Event to {repository} - {commits} commits")
    
    else:
        print(f"📨 Received event: {event_type}")
    
    return {"status": "received", "event": event_type}