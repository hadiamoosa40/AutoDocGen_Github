from fastapi import Request, HTTPException
from jose import jwt
from config import JWT_SECRET

async def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Missing token")

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        request.state.user = payload
    except:
        raise HTTPException(401, "Invalid token")