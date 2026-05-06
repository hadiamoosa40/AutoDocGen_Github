import json
from typing import Dict, List
from fastapi import WebSocket
import asyncio


class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        # user_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"🔌 WS connected: user={user_id} total={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"🔌 WS disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a JSON message to all connections of a user."""
        if user_id not in self.active_connections:
            return
        dead = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d, user_id)

    async def broadcast(self, message: dict):
        """Send a message to ALL connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)

    def get_connected_users(self) -> List[str]:
        return list(self.active_connections.keys())

    def is_user_connected(self, user_id: str) -> bool:
        return user_id in self.active_connections and bool(self.active_connections[user_id])


# Singleton instance
ws_manager = ConnectionManager()