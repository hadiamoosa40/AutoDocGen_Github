from jose import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET

def create_token(data):
    data["exp"] = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])