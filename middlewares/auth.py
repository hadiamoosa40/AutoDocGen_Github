from fastapi import Request, HTTPException
from services.jwt import decode_token

def get_user_from_cookie(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(401, "Not authenticated")

    return decode_token(token)["id"]