from fastapi import FastAPI, WebSocket
from routes import auth, repos, webhook
from ws.manager import manager
app = FastAPI()

app.include_router(auth.router)
app.include_router(repos.router)
app.include_router(webhook.router)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        manager.disconnect(ws)