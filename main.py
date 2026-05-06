from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, github, webhook

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # local frontend
        "https://autodocgengithub-production.up.railway.app"  # optional (same backend)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(github.router, prefix="/github")
app.include_router(webhook.router)