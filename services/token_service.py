from datetime import datetime
from db import get_users_collection
from utils.jwt_utils import create_access_token, create_refresh_token

class TokenService:
    @staticmethod
    async def save_user_token(github_id: int, access_token: str, refresh_token: str = None):
        """Save user token in database"""
        users_collection = await get_users_collection()
        await users_collection.update_one(
            {"github_id": github_id},
            {
                "$set": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "last_login": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> dict:
        """Generate new access token from refresh token"""
        from utils.jwt_utils import verify_token
        
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"github_id": payload.get("user_id")})
        
        if not user:
            return None
        
        new_access_token = create_access_token({"user_id": user["github_id"], "username": user["username"]})
        return {"access_token": new_access_token}

token_service = TokenService()