from fastapi import Header, HTTPException
from utils.jwt import verify_token


def get_current_user(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(401, "Missing token")

    token = authorization.replace("Bearer ", "")

    try:
        return verify_token(token)
    except:
        raise HTTPException(401, "Invalid token")