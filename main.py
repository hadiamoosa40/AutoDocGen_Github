import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from db.database import connect_db, disconnect_db
from routes.auth import router as auth_router
from routes.repos import router as repos_router
from routes.webhooks import router as webhooks_router
from routes.ws import router as ws_router
from middlewares.rate_limiter import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()

app = FastAPI(
    title="AutoDoc Gen GitHub API",
    description="GitHub Integration API with OAuth, Webhooks, and WebSockets",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(RateLimitMiddleware)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(repos_router, prefix="/repos", tags=["Repositories"])
app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(ws_router, prefix="/ws", tags=["WebSockets"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AutoDoc Gen GitHub API"}