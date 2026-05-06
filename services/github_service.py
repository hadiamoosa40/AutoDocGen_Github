import httpx
import os
from typing import Dict, Any, List, Optional

class GitHubService:
    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange OAuth code for access token"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                return None
        except Exception as e:
            print(f"Error exchanging code: {e}")
            return None
    
    async def get_github_user(self, access_token: str) -> Optional[Dict]:
        """Get GitHub user information"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def get_user_repos(self, access_token: str) -> List[Dict]:
        """Get user repositories"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.github.com/user/repos",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"per_page": 100, "sort": "updated", "direction": "desc"}
                )
                
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            print(f"Error getting repos: {e}")
            return []

github_service = GitHubService()