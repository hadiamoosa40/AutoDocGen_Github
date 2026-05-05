import httpx
from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI

async def exchange_code(code: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        data = res.json()
        print("TOKEN RESPONSE:", data)
        return data.get("access_token")


async def get_user(token: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        data = res.json()
        print("USER RESPONSE:", data)
        return data