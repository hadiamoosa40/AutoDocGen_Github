from fastapi import APIRouter, HTTPException, Depends
from db import get_user, update_user
from middlewares.auth_middleware import get_current_user
import requests
import os
import jwt
import time

router = APIRouter()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

def generate_jwt():
    """Generate JWT for GitHub App"""
    if not GITHUB_APP_ID or not GITHUB_PRIVATE_KEY:
        return None
    
    private_key = GITHUB_PRIVATE_KEY
    if "-----BEGIN RSA PRIVATE KEY-----" not in private_key:
        private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
    
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": int(GITHUB_APP_ID)
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_token(installation_id):
    """Get installation access token"""
    jwt_token = generate_jwt()
    
    if not jwt_token:
        return None
    
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
    )
    
    if response.status_code == 201:
        return response.json().get("token")
    return None

@router.get("/github/install")
def install_app():
    """Redirect to GitHub App installation"""
    app_name = os.getenv("GITHUB_APP_NAME", "AutodocGen")
    install_url = f"https://github.com/apps/{app_name}/installations/new"
    return {"install_url": install_url}

@router.get("/github/callback")
def github_callback(installation_id: int, current_user: dict = Depends(get_current_user)):
    """Handle GitHub App installation callback"""
    user_id = current_user.get("user_id")
    
    # Update user with installation ID
    update_user(user_id, {"installation_id": installation_id})
    
    print(f"✅ GitHub App installed: installation_id={installation_id} for user={user_id}")
    
    return {"success": True, "message": "App installed successfully"}

@router.get("/github/repos")
def get_repos(current_user: dict = Depends(get_current_user)):
    """Get all repositories for the user"""
    user_id = current_user.get("user_id")
    user = get_user(user_id)
    
    if not user:
        raise HTTPException(404, "User not found")
    
    # If user has installation, use installation token
    if user.get("installation_id"):
        token = get_installation_token(user["installation_id"])
        if token:
            response = requests.get(
                "https://api.github.com/installation/repositories",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                repos = response.json().get("repositories", [])
                return {
                    "installed": True,
                    "repositories": repos
                }
    
    # Fallback to user token
    github_token = user.get("github_token")
    if github_token:
        response = requests.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        
        if response.status_code == 200:
            repos = response.json()
            return {
                "installed": False,
                "repositories": repos,
                "message": "Install GitHub App for better integration"
            }
    
    return {
        "installed": False,
        "repositories": [],
        "install_url": f"https://github.com/apps/{os.getenv('GITHUB_APP_NAME', 'AutodocGen')}/installations/new"
    }

@router.get("/github/repo/{owner}/{repo_name}")
def get_repo_data(owner: str, repo_name: str, current_user: dict = Depends(get_current_user)):
    """Get specific repository data and print to backend"""
    user_id = current_user.get("user_id")
    user = get_user(user_id)
    
    if not user:
        raise HTTPException(404, "User not found")
    
    print(f"\n{'='*70}")
    print(f"🔥 FETCHING DATA FOR REPOSITORY: {owner}/{repo_name}")
    print(f"{'='*70}")
    
    repo_data = None
    
    # Try with installation token first
    if user.get("installation_id"):
        token = get_installation_token(user["installation_id"])
        if token:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo_name}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                repo_data = response.json()
    
    # Fallback to user token
    if not repo_data and user.get("github_token"):
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers={"Authorization": f"Bearer {user['github_token']}"}
        )
        
        if response.status_code == 200:
            repo_data = response.json()
    
    if not repo_data:
        raise HTTPException(404, f"Repository {owner}/{repo_name} not found")
    
    # Print all data to backend console
    print(f"\n📦 REPOSITORY INFORMATION:")
    print(f"   • Name: {repo_data.get('name')}")
    print(f"   • Full Name: {repo_data.get('full_name')}")
    print(f"   • Owner: {repo_data.get('owner', {}).get('login')}")
    print(f"   • Description: {repo_data.get('description', 'No description')}")
    print(f"   • Stars: ⭐ {repo_data.get('stargazers_count', 0)}")
    print(f"   • Forks: 🍴 {repo_data.get('forks_count', 0)}")
    print(f"   • Open Issues: ⚠️ {repo_data.get('open_issues_count', 0)}")
    print(f"   • Language: {repo_data.get('language', 'Not specified')}")
    print(f"   • Default Branch: {repo_data.get('default_branch')}")
    print(f"   • Size: {repo_data.get('size', 0)} KB")
    print(f"   • Watchers: {repo_data.get('watchers_count', 0)}")
    print(f"   • Created: {repo_data.get('created_at')}")
    print(f"   • Last Push: {repo_data.get('pushed_at')}")
    print(f"   • URL: {repo_data.get('html_url')}")
    print(f"   • Clone URL: {repo_data.get('clone_url')}")
    
    if repo_data.get('license'):
        print(f"   • License: {repo_data['license'].get('name')}")
    
    if repo_data.get('topics'):
        print(f"   • Topics: {', '.join(repo_data['topics'])}")
    
    print(f"\n📊 ADDITIONAL STATS:")
    print(f"   • Subscribers: {repo_data.get('subscribers_count', 0)}")
    print(f"   • Network Count: {repo_data.get('network_count', 0)}")
    
    print(f"\n{'='*70}")
    print(f"✅ DATA FETCHED SUCCESSFULLY FOR: {owner}/{repo_name}")
    print(f"{'='*70}\n")
    
    return {
        "success": True,
        "message": f"✅ Data fetched successfully for {owner}/{repo_name}",
        "data": repo_data
    }