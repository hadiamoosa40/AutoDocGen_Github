from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.jwt_handler import verify_token
from app.db import get_collection
from app.models.user import User

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request) -> User:
    # Get token from header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = auth_header.split(" ")[1]
    
    # Verify token
    payload = verify_token(token)
    github_id = payload.get("github_id")
    
    if not github_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    collection = get_collection("users")
    user_data = await collection.find_one({"github_id": github_id})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return User(**user_data)

async def verify_websocket_token(token: str) -> Optional[str]:
    try:
        payload = verify_token(token)
        github_id = payload.get("github_id")
        
        # Verify user exists
        collection = get_collection("users")
        user_data = await collection.find_one({"github_id": github_id})
        
        if user_data:
            return str(github_id)
        
        return None
    except:
        return None