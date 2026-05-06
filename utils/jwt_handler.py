from jose import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET

ALGO = "HS256"


def create_access_token(data):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=15)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)


def create_refresh_token(data):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)