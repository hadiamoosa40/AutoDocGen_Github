from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from utils.ws_manager import ws_manager
from utils.jwt_utils import verify_access_token

router = APIRouter()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint. Client connects with:
      ws://host/ws/connect?token=<access_token>
    """
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected as user {user_id}",
            "user_id": user_id,
        })

        # Keep connection alive - listen for ping/pong
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "subscribe":
                repo = data.get("repo")
                await websocket.send_json({
                    "type": "subscribed",
                    "repo": repo,
                    "message": f"Subscribed to events for {repo}",
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        ws_manager.disconnect(websocket, user_id)