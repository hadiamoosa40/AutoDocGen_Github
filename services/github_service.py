from jose import jwt
import time
import requests
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

def generate_jwt():
    # Handle private key with proper formatting
    private_key = PRIVATE_KEY
    if "-----BEGIN RSA PRIVATE KEY-----" not in private_key:
        private_key = "-----BEGIN RSA PRIVATE KEY-----\n" + private_key + "\n-----END RSA PRIVATE KEY-----"
    
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": APP_ID
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")


# 2. Get installation token
def get_installation_token(installation_id: int):

    jwt_token = generate_jwt()

    res = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
    )

    data = res.json()

    if "token" not in data:
        raise Exception(f"GitHub token error: {data}")

    return data["token"]
# 3. Fetch repos
def get_repos(installation_id: int):

    token = get_installation_token(installation_id)

    res = requests.get(
        "https://api.github.com/installation/repositories",
        headers={"Authorization": f"Bearer {token}"}
    )

    return res.json()["repositories"]


# 4. Fetch single repo
def get_repo(installation_id: int, owner: str, repo: str):

    token = get_installation_token(installation_id)

    res = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers={"Authorization": f"Bearer {token}"}
    )

    return res.json()