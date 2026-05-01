users_collection.update_one(
    {"github_id": user["id"]},
    {
        "$set": {
            "github_id": user["id"],
            "username": user["login"],
            "avatar": user["avatar_url"],
            "github_token": github_token
        }
    },
    upsert=True
)