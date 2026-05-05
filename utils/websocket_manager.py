from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    async def broadcast(self, msg: dict):
        for c in self.connections:
            await c.send_json(msg)


manager = WSManager()