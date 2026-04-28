from fastapi import APIRouter, Request
from utils.websocket_manager import manager

router = APIRouter()


@router.post("/webhook/github")
async def webhook(req: Request):

    data = await req.json()
    event = req.headers.get("X-GitHub-Event")

    if event == "push":

        msg = {
            "type": "push",
            "repo": data["repository"]["full_name"],
            "user": data["pusher"]["name"]
        }

        await manager.broadcast(msg)

    return {"ok": True}