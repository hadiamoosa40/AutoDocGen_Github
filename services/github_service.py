import jwt
import time
import requests
import os
from datetime import datetime

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

def generate_jwt():
    """Generate JWT for GitHub App"""
    if not APP_ID or not PRIVATE_KEY:
        raise Exception("GitHub App credentials missing")
    
    # Format private key properly
    private_key = PRIVATE_KEY
    if "-----BEGIN RSA PRIVATE KEY-----" not in private_key:
        private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
    
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,  # 10 minutes expiration
        "iss": int(APP_ID)
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_token(installation_id: int):
    """Get installation access token"""
    try:
        jwt_token = generate_jwt()
        
        response = requests.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to get installation token: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get installation token: {response.text}")
        
        data = response.json()
        token = data.get("token")
        
        if not token:
            raise Exception(f"No token in response: {data}")
        
        print(f"✅ Installation token obtained successfully")
        return token
        
    except Exception as e:
        print(f"❌ Error getting installation token: {str(e)}")
        raise

def get_user_repos(installation_id: int):
    """Get all repositories for the installation"""
    try:
        token = get_installation_token(installation_id)
        
        response = requests.get(
            "https://api.github.com/installation/repositories",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get repos: {response.status_code}")
            return []
        
        data = response.json()
        repos = data.get("repositories", [])
        print(f"📚 Found {len(repos)} repositories")
        
        return repos
        
    except Exception as e:
        print(f"❌ Error getting repos: {str(e)}")
        return []

def get_repo_data(installation_id: int, owner: str, repo_name: str):
    """Get detailed data for a specific repository"""
    try:
        token = get_installation_token(installation_id)
        
        # Fetch repository details
        repo_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        
        if repo_response.status_code != 200:
            print(f"❌ Failed to get repo data: {repo_response.status_code}")
            return None
        
        repo_data = repo_response.json()
        
        # Log the fetched data to backend console
        print(f"\n{'='*60}")
        print(f"🔥 DATA FETCHED FOR REPO: {owner}/{repo_name}")
        print(f"{'='*60}")
        print(f"📦 Repository Name: {repo_data.get('name')}")
        print(f"👤 Owner: {repo_data.get('owner', {}).get('login')}")
        print(f"📝 Description: {repo_data.get('description', 'No description')}")
        print(f"⭐ Stars: {repo_data.get('stargazers_count')}")
        print(f"🍴 Forks: {repo_data.get('forks_count')}")
        print(f"⚠️ Open Issues: {repo_data.get('open_issues_count')}")
        print(f"🔧 Language: {repo_data.get('language')}")
        print(f"📅 Created: {repo_data.get('created_at')}")
        print(f"🔄 Last Push: {repo_data.get('pushed_at')}")
        print(f"🌐 URL: {repo_data.get('html_url')}")
        print(f"{'='*60}\n")
        
        return repo_data
        
    except Exception as e:
        print(f"❌ Error getting repo data: {str(e)}")
        return None

def get_repo_contents(installation_id: int, owner: str, repo_name: str, path: str = ""):
    """Get contents of a repository"""
    try:
        token = get_installation_token(installation_id)
        
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get repo contents: {response.status_code}")
            return []
        
        return response.json()
        
    except Exception as e:
        print(f"❌ Error getting repo contents: {str(e)}")
        return []