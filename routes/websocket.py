from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.websocket_manager import manager
from app.middlewares.auth_middleware import verify_websocket_token
import json

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    # Get token from query params
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    
    # Verify token and get user
    user_id = await verify_websocket_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to real-time updates",
            "user_id": user_id
        })
        
        # Listen for messages from client
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)