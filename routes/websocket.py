from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.websocket_manager import manager
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"📨 WebSocket message received: {data}")
            
            # Echo back
            await websocket.send_json({
                "type": "ping",
                "message": "Connection active"
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)