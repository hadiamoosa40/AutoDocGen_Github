from fastapi import FastAPI
from routes import auth, github, webhook
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/auth")
app.include_router(github.router, prefix="/github")
app.include_router(webhook.router)