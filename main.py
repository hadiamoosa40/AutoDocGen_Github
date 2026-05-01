from fastapi import FastAPI
from routes import github_app, github, webhook, websocket
from fastapi.middleware.cors import CORSMiddleware
from routes import dashboard

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_app.router)
app.include_router(github.router)
app.include_router(webhook.router)
app.include_router(websocket.router)
app.include_router(dashboard.router)