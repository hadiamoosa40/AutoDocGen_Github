from fastapi import APIRouter, Request, HTTPException
import hmac, hashlib
from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()

@router.post("/webhook")
async def webhook(req: Request):
    body = await req.body()
    sig = req.headers.get("X-Hub-Signature-256")

    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256)
    if not hmac.compare_digest("sha256=" + mac.hexdigest(), sig):
        raise HTTPException(403)

    return {"ok": True}