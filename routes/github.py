from fastapi import APIRouter, HTTPException, Request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# In-memory storage for user tokens
user_tokens = {}

@router.post("/github/store-token")
def store_token(token: str, username: str):
    """Store user token"""
    # Extract user info from token if needed
    try:
        # Get user info from GitHub to verify
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get("login")
            print(f"👤 Verified user: {username}")
    except:
        pass
    
    user_tokens[username] = {
        "token": token,
        "username": username
    }
    print(f"💾 Token stored for user: {username}")
    print(f"📊 Total users: {len(user_tokens)}")
    return {"success": True, "username": username}

@router.get("/github/repos")
def get_repos(username: str = None, request: Request = None):
    """Get all repositories for the user - username is now optional"""
    print(f"📚 Getting repos request received")
    
    # If username not provided, try to get from token in header
    if not username and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # Find user by token
            for stored_username, user_data in user_tokens.items():
                if user_data["token"] == token:
                    username = stored_username
                    print(f"🔍 Found username from token: {username}")
                    break
    
    if not username:
        print("❌ No username provided in request")
        return {
            "error": "Username required",
            "installed": False,
            "repositories": []
        }
    
    print(f"📚 Getting repos for user: {username}")
    
    # Get user's stored token
    user_data = user_tokens.get(username)
    
    if not user_data:
        print(f"❌ No token found for user: {username}")
        return {
            "installed": False,
            "repositories": [],
            "message": "Not authenticated. Please login again.",
            "install_url": f"https://github.com/apps/{os.getenv('GITHUB_APP_NAME', 'AutodocGen')}/installations/new"
        }
    
    github_token = user_data["token"]
    
    try:
        # Get user's repositories
        response = requests.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {github_token}"},
            params={"per_page": 100, "sort": "updated", "direction": "desc"},
            timeout=10
        )
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos)} repositories for {username}")
            
            # Format repository data
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "html_url": repo.get("html_url"),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "open_issues_count": repo.get("open_issues_count", 0),
                    "language": repo.get("language"),
                    "owner": {
                        "login": repo.get("owner", {}).get("login"),
                        "avatar_url": repo.get("owner", {}).get("avatar_url")
                    },
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at")
                })
            
            # Check if GitHub App is installed (optional)
            has_installation = False
            try:
                install_response = requests.get(
                    "https://api.github.com/user/installations",
                    headers={
                        "Authorization": f"Bearer {github_token}",
                        "Accept": "application/vnd.github+json"
                    },
                    timeout=10
                )
                if install_response.status_code == 200:
                    installations = install_response.json()
                    has_installation = len(installations.get("installations", [])) > 0
            except:
                pass
            
            return {
                "installed": has_installation,
                "repositories": formatted_repos,
                "username": username,
                "total_count": len(formatted_repos)
            }
        else:
            print(f"❌ Failed to get repos: {response.status_code} - {response.text}")
            return {
                "installed": False,
                "repositories": [],
                "message": f"Failed to fetch repositories. Status: {response.status_code}",
                "install_url": f"https://github.com/apps/{os.getenv('GITHUB_APP_NAME', 'AutodocGen')}/installations/new"
            }
            
    except Exception as e:
        print(f"❌ Error getting repos: {str(e)}")
        return {
            "installed": False,
            "repositories": [],
            "message": str(e)
        }

@router.get("/github/repo/{owner}/{repo_name}")
def get_repo_data(owner: str, repo_name: str, username: str = None, request: Request = None):
    """Get specific repository data and print to backend"""
    print(f"\n{'='*70}")
    print(f"🔥 FETCHING DATA FOR REPOSITORY: {owner}/{repo_name}")
    print(f"{'='*70}")
    
    # If username not provided, try to get from token in header
    if not username and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # Find user by token
            for stored_username, user_data in user_tokens.items():
                if user_data["token"] == token:
                    username = stored_username
                    print(f"🔍 Found username from token: {username}")
                    break
    
    if not username:
        print("❌ No username provided")
        raise HTTPException(400, "Username required")
    
    # Get user's stored token
    user_data = user_tokens.get(username)
    
    if not user_data:
        print(f"❌ No token found for user: {username}")
        raise HTTPException(401, "Not authenticated")
    
    github_token = user_data["token"]
    
    try:
        # Get repository data
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers={"Authorization": f"Bearer {github_token}"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get repo: {response.status_code}")
            raise HTTPException(404, f"Repository {owner}/{repo_name} not found")
        
        repo_data = response.json()
        
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
        
        if repo_data.get('license'):
            print(f"   • License: {repo_data['license'].get('name')}")
        
        if repo_data.get('topics'):
            topics = repo_data['topics']
            print(f"   • Topics: {', '.join(topics[:5])}")
        
        # Get languages
        try:
            lang_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo_name}/languages",
                headers={"Authorization": f"Bearer {github_token}"},
                timeout=10
            )
            if lang_response.status_code == 200:
                languages = lang_response.json()
                if languages:
                    print(f"   • Languages: {', '.join(list(languages.keys())[:5])}")
        except:
            pass
        
        # Get README
        try:
            readme_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo_name}/readme",
                headers={"Authorization": f"Bearer {github_token}"},
                timeout=10
            )
            if readme_response.status_code == 200:
                print(f"   • Has README: ✅ Yes")
        except:
            pass
        
        print(f"\n{'='*70}")
        print(f"✅ DATA FETCHED SUCCESSFULLY FOR: {owner}/{repo_name}")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "message": f"✅ Data fetched successfully for {owner}/{repo_name}",
            "data": repo_data
        }
        
    except requests.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        raise HTTPException(500, f"Error fetching repository data: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(500, str(e))

@router.get("/github/install")
def install_app():
    """Get GitHub App installation URL"""
    app_name = os.getenv("GITHUB_APP_NAME", "AutodocGen")
    install_url = f"https://github.com/apps/{app_name}/installations/new"
    print(f"🔧 Returning install URL: {install_url}")
    return {"install_url": install_url}

@router.get("/github/callback")
def github_callback(installation_id: int, username: str = None):
    """Handle GitHub App installation callback"""
    print(f"✅ GitHub App installed: installation_id={installation_id}")
    return {"success": True, "message": "App installed successfully"}

@router.get("/github/current-user")
def get_current_user(request: Request):
    """Get current user from token"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        for username, user_data in user_tokens.items():
            if user_data["token"] == token:
                return {"authenticated": True, "username": username}
    return {"authenticated": False}