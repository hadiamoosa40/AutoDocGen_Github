from fastapi import Header, HTTPException
from utils.jwt import decode_token

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        return decode_token(authorization)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")