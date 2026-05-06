import httpx
import jwt
import time
import os
from typing import Dict, Any, List, Optional

class GitHubService:
    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key = os.getenv("GITHUB_PRIVATE_KEY")
    
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
    
    async def get_repo_contents(self, access_token: str, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get repository contents"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            print(f"Error getting repo contents: {e}")
            return []
    
    async def get_file_content(self, access_token: str, owner: str, repo: str, path: str) -> Optional[str]:
        """Get file content from repository"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    import base64
                    if data.get("content"):
                        return base64.b64decode(data["content"]).decode('utf-8')
                return None
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None
    
    def generate_jwt_for_app(self) -> Optional[str]:
        """Generate JWT for GitHub App"""
        if not self.app_id or not self.private_key:
            return None
        
        try:
            # Format private key correctly
            private_key = self.private_key
            if "-----BEGIN RSA PRIVATE KEY-----" not in private_key:
                private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
            
            payload = {
                "iat": int(time.time()),
                "exp": int(time.time()) + 600,  # 10 minutes expiration
                "iss": int(self.app_id)
            }
            
            return jwt.encode(payload, private_key, algorithm="RS256")
        except Exception as e:
            print(f"Error generating JWT: {e}")
            return None

github_service = GitHubService()