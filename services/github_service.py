import requests
import base64
from db import users_collection

# -----------------------------
# GET ALL REPOS
# -----------------------------
def get_user_repos(token: str):
    res = requests.get(
        "https://api.github.com/user/repos",
        headers={"Authorization": f"Bearer {token}"}
    )
    return res.json()


# -----------------------------
# RECURSIVE FILE FETCH (IMPORTANT)
# -----------------------------
def fetch_repo_files(token, owner, repo, path=""):

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    res = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )

    data = res.json()
    files = []

    for item in data:

        # FILE
        if item["type"] == "file":

            file_data = requests.get(item["download_url"])

            files.append({
                "path": item["path"],
                "content": file_data.text
            })

        # DIRECTORY (RECURSION)
        elif item["type"] == "dir":
            files.extend(
                fetch_repo_files(token, owner, repo, item["path"])
            )

    return files


# -----------------------------
# GET SINGLE REPO FULL CODE
# -----------------------------
def get_repo_code(token, owner, repo):
    return fetch_repo_files(token, owner, repo)