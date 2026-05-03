from fastapi import Header, HTTPException, Depends
from utils.jwt import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = authorization.credentials
        payload = verify_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
            
        return payload
    except Exception as e:
        raise HTTPException(401, str(e))