import httpx

async def get_repos(token: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {token}"},
        )
        return res.json()


async def get_repo_contents(token: str, owner: str, repo: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents",
            headers={"Authorization": f"Bearer {token}"},
        )
        return res.json()