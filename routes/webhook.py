from fastapi import APIRouter, Request
import hmac, hashlib

from db import users
from config import GITHUB_WEBHOOK_SECRET

router = APIRouter()

@router.post("/webhook")
async def webhook(req: Request):

    body = await req.body()
    signature = req.headers.get("X-Hub-Signature-256")

    mac = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    )

    if not hmac.compare_digest("sha256=" + mac.hexdigest(), signature):
        return {"error": "invalid signature"}

    payload = await req.json()

    installation_id = payload.get("installation", {}).get("id")
    sender_id = payload["sender"]["id"]

    await users.update_one(
        {"github_id": sender_id},
        {"$set": {"installation_id": installation_id}}
    )

    return {"ok": True}