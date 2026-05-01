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