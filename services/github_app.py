import jwt, time, httpx
from config import GITHUB_APP_ID, GITHUB_PRIVATE_KEY

# Create GitHub App JWT

def app_jwt():
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": GITHUB_APP_ID
    }
    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")


# Get installation token
async def installation_token(installation_id):
    token = app_jwt()

    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={"Authorization": f"Bearer {token}"}
        )
        return r.json()["token"]


# Get repos
async def get_repos(token):
    async with httpx.AsyncClient() as c:
        r = await c.get(
            "https://api.github.com/installation/repositories",
            headers={"Authorization": f"Bearer {token}"}
        )
        return r.json()