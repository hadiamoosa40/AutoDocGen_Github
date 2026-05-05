from fastapi import APIRouter, Request
from utils.websocket_manager import manager

router = APIRouter()


@router.post("/webhook/github")
async def webhook(request: Request):

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    if event == "push":

        repo = payload["repository"]["full_name"]

        await manager.broadcast({
            "type": "repo_updated",
            "repo": repo,
            "message": "Code updated on GitHub"
        })

    return {"ok": True}