from fastapi import APIRouter, Request
from db import users_collection
from utils.websocket_manager import manager

router = APIRouter()

@router.post("/webhook/github")
async def webhook(req: Request):

    data = await req.json()
    event = req.headers.get("X-GitHub-Event")

    repo = data.get("repository", {}).get("full_name")

    print(f"🔥 EVENT: {event} from {repo}")

    # 🔥 AUTO SYNC TRIGGER
    if event in ["push", "installation_repositories", "installation"]:

        await manager.broadcast({
            "type": "refresh_repos"
        })

    return {"ok": True}