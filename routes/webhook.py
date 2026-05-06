from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from db import get_webhook_events_collection
from datetime import datetime
import hmac
import hashlib
import os

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

async def process_webhook_event(event_type: str, payload: dict):
    """Process webhook events in background"""
    webhook_events = await get_webhook_events_collection()
    
    # Store webhook event
    await webhook_events.insert_one({
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.utcnow(),
        "processed": False
    })
    
    # Handle different event types
    if event_type == "push":
        print(f"📝 Push event received for {payload.get('repository', {}).get('full_name')}")
        # Trigger document generation here
        await trigger_document_generation(payload)
    
    elif event_type == "pull_request":
        print(f"🔄 PR event received: {payload.get('action')}")
    
    elif event_type == "issues":
        print(f"🐛 Issue event received: {payload.get('action')}")

async def trigger_document_generation(payload: dict):
    """Trigger document generation using LangChain"""
    # This will be implemented for LLM integration
    print(f"🚀 Triggering document generation for {payload.get('repository', {}).get('full_name')}")
    # TODO: Add LangChain integration here

@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events"""
    # Verify webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    if webhook_secret and signature:
        body = await request.body()
        expected_signature = "sha256=" + hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(401, "Invalid webhook signature")
    
    # Get event type
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()
    
    # Process webhook in background
    background_tasks.add_task(process_webhook_event, event_type, payload)
    
    return {"status": "received", "event": event_type}