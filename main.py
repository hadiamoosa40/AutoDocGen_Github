from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, github, github_app, webhook

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(github.router)
app.include_router(github_app.router)
app.include_router(webhook.router)


@app.get("/")
def root():
    return {"status": "AutoDocGen running"}