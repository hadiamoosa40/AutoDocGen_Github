from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws")
async def ws(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)