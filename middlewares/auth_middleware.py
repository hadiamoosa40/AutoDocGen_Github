# middlewares/auth_middleware.py

from fastapi import Header, HTTPException
from utils.jwt import verify_token

def get_current_user(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(401, "No token")

    token = authorization.split(" ")[1]

    try:
        payload = verify_token(token)
        return payload
    except:
        raise HTTPException(401, "Invalid token")