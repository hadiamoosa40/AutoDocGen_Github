from jose import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET

def create_token(user_id):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")