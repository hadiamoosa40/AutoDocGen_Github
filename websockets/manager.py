from fastapi import WebSocket

class Manager:
    def __init__(self):
        self.connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self.connections.remove(ws)

    async def broadcast(self, data):
        for ws in self.connections:
            await ws.send_json(data)

manager = Manager()