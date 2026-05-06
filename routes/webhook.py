from fastapi import APIRouter, Request
import hmac, hashlib
from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()

@router.post("/webhook")
async def webhook(req: Request):
    body = await req.body()
    sig = req.headers.get("X-Hub-Signature-256")

    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256)

    if not hmac.compare_digest("sha256=" + mac.hexdigest(), sig):
        return {"error": "invalid"}

    payload = await req.json()

    return {
        "installation_id": payload.get("installation", {}).get("id")
    }