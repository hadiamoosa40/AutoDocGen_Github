from fastapi import APIRouter, Request, Header, HTTPException
from utils.crypto import verify_signature
from ws.manager import manager
from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()

@router.post("/webhook/github")
async def webhook(request: Request, x_hub_signature_256: str = Header(None)):
    body = await request.body()

    if not verify_signature(GITHUB_WEBHOOK_SECRET, body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    await manager.broadcast({
        "event": event,
        "repo": payload.get("repository", {}).get("full_name")
    })

    return {"ok": True}