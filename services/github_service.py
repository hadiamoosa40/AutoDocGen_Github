import httpx

BASE = "https://api.github.com"

async def exchange_code(code, cid, secret):
    async with httpx.AsyncClient() as c:
        r = await c.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": cid, "client_secret": secret, "code": code}
        )
        return r.json()

async def get_user(token):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/user", headers={"Authorization": f"Bearer {token}"})
        return r.json()

async def get_repos(token):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/user/repos", headers={"Authorization": f"Bearer {token}"})
        return r.json()

async def get_tree(token, owner, repo):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
                        headers={"Authorization": f"Bearer {token}"})
        return r.json()