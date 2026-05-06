from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import Database
from routes import auth_router, github_router, webhook_router, websocket_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.connect_db()
    print("🚀 Application started")
    yield
    # Shutdown
    await Database.close_db()
    print("👋 Application shutdown")

app = FastAPI(
    title="GitHub Integration API",
    description="Production-grade GitHub integration with JWT, WebSockets, and Webhooks",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(github_router)
app.include_router(webhook_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {
        "message": "GitHub Integration API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)