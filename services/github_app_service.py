import jwt
import time
import httpx
from config import GITHUB_APP_ID, GITHUB_PRIVATE_KEY

def generate_app_jwt():
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": GITHUB_APP_ID
    }
    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")

async def get_installation_token(installation_id):
    app_jwt = generate_app_jwt()

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json"
            }
        )
        return res.json()["token"]

async def get_repos(token):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/installation/repositories",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()

async def get_tree(token, owner, repo):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()