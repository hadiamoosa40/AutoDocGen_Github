from fastapi import APIRouter, WebSocket

router = APIRouter()
connections = []


@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    connections.append(ws)

    while True:
        await ws.receive_text()