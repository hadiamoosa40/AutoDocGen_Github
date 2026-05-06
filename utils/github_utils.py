import os
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI",
    "https://autodocgengithub-production.up.railway.app/auth/github/callback"
)
GITHUB_SCOPES = "read:user user:email repo admin:repo_hook"


def get_github_oauth_url(state: str) -> str:
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": GITHUB_SCOPES,
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://github.com/login/oauth/authorize?{query}"


async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
            timeout=15.0,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for GitHub token",
        )
    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub OAuth error: {data.get('error_description', 'Unknown error')}",
        )
    return access_token


async def get_github_user(github_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=15.0,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to fetch GitHub user info",
        )
    return response.json()


async def get_github_user_emails(github_token: str) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )
    if response.status_code != 200:
        return []
    return response.json()


async def get_github_repos(github_token: str, page: int = 1, per_page: int = 30) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "type": "all",
            },
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch repositories from GitHub",
        )
    return response.json()


async def get_repo_contents(github_token: str, owner: str, repo: str, path: str = "") -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Path not found in repository")
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch repository contents",
        )
    return response.json()


async def get_file_content(github_token: str, download_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            download_url,
            headers={"Authorization": f"Bearer {github_token}"},
            timeout=30.0,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch file content",
        )
    return response.text


async def create_webhook(github_token: str, owner: str, repo: str, webhook_url: str, secret: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/hooks",
            json={
                "name": "web",
                "active": True,
                "events": ["push", "pull_request", "create", "delete", "release"],
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "secret": secret,
                    "insecure_ssl": "0",
                },
            },
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )
    if response.status_code not in (200, 201):
        error_data = response.json()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create webhook: {error_data.get('message', 'Unknown error')}",
        )
    return response.json()


async def delete_webhook(github_token: str, owner: str, repo: str, hook_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )
    if response.status_code not in (204, 404):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete webhook",
        )