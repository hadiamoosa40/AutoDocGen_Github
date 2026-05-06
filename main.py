from fastapi import FastAPI
from routes import auth, github, webhook, websocket

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(github.router, prefix="/github")
app.include_router(webhook.router)
app.include_router(websocket.router)