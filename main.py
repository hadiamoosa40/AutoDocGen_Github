from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, github_app, github, webhook, websocket, dashboard
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GitHub Integration App")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "https://your-frontend.vercel.app"), "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(github_app.router)
app.include_router(github.router)
app.include_router(webhook.router)
app.include_router(websocket.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "GitHub Integration API is running", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}