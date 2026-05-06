import asyncio
import base64
from typing import Optional
import httpx
from fastapi import HTTPException

from utils.github_utils import (
    get_github_repos,
    get_repo_contents,
    get_file_content,
)

# Extensions we care about for code documentation
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
    ".md", ".yaml", ".yml", ".json", ".toml", ".env.example",
    ".sh", ".bash", ".sql", ".graphql", ".proto",
}

# Directories to skip
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage", ".pytest_cache",
}

MAX_FILE_SIZE_BYTES = 500_000  # 500 KB per file


async def list_user_repos(github_token: str, page: int = 1, per_page: int = 30) -> list:
    repos = await get_github_repos(github_token, page=page, per_page=per_page)
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "full_name": r["full_name"],
            "description": r.get("description"),
            "private": r["private"],
            "language": r.get("language"),
            "default_branch": r.get("default_branch", "main"),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "updated_at": r.get("updated_at"),
            "html_url": r["html_url"],
            "size": r.get("size", 0),
        }
        for r in repos
    ]


async def get_repo_tree(github_token: str, owner: str, repo: str, path: str = "") -> list:
    """Recursively list repo contents (breadth-first, respecting skip list)."""
    contents = await get_repo_contents(github_token, owner, repo, path)
    if isinstance(contents, dict):
        # Single file response
        return [_format_content_item(contents)]

    result = []
    for item in contents:
        if item["type"] == "dir":
            if item["name"] in SKIP_DIRS:
                continue
            result.append({
                "name": item["name"],
                "path": item["path"],
                "type": "dir",
                "children": [],  # Lazy loaded on demand
            })
        else:
            result.append(_format_content_item(item))
    return result


def _format_content_item(item: dict) -> dict:
    ext = ""
    if "." in item.get("name", ""):
        ext = "." + item["name"].rsplit(".", 1)[-1].lower()
    return {
        "name": item["name"],
        "path": item["path"],
        "type": item["type"],
        "size": item.get("size", 0),
        "download_url": item.get("download_url"),
        "sha": item.get("sha"),
        "extension": ext,
        "is_code": ext in CODE_EXTENSIONS,
    }


async def fetch_file_content(github_token: str, owner: str, repo: str, file_path: str) -> dict:
    """Fetch content of a single file."""
    contents = await get_repo_contents(github_token, owner, repo, file_path)

    if isinstance(contents, list):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")

    # Check size
    size = contents.get("size", 0)
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size} bytes). Max allowed: {MAX_FILE_SIZE_BYTES}",
        )

    # Decode base64 content if available
    if contents.get("content") and contents.get("encoding") == "base64":
        try:
            raw = base64.b64decode(contents["content"]).decode("utf-8", errors="replace")
        except Exception:
            raw = "[Binary file - cannot display]"
    elif contents.get("download_url"):
        raw = await get_file_content(github_token, contents["download_url"])
    else:
        raw = "[Content unavailable]"

    return {
        "name": contents["name"],
        "path": contents["path"],
        "content": raw,
        "size": size,
        "sha": contents.get("sha"),
        "encoding": contents.get("encoding", "utf-8"),
    }


async def fetch_all_code_files(
    github_token: str,
    owner: str,
    repo: str,
    path: str = "",
    collected: Optional[list] = None,
    depth: int = 0,
    max_depth: int = 8,
) -> list:
    """Recursively fetch all code files in a repo for LangChain ingestion."""
    if collected is None:
        collected = []
    if depth > max_depth:
        return collected

    try:
        contents = await get_repo_contents(github_token, owner, repo, path)
    except Exception:
        return collected

    if isinstance(contents, dict):
        contents = [contents]

    tasks = []
    dirs_to_recurse = []

    for item in contents:
        if item["type"] == "dir":
            if item["name"] not in SKIP_DIRS:
                dirs_to_recurse.append(item["path"])
        elif item["type"] == "file":
            ext = ""
            if "." in item.get("name", ""):
                ext = "." + item["name"].rsplit(".", 1)[-1].lower()
            if ext in CODE_EXTENSIONS and item.get("size", 0) <= MAX_FILE_SIZE_BYTES:
                tasks.append(fetch_file_content(github_token, owner, repo, item["path"]))

    # Fetch files concurrently
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, dict):
                collected.append(r)

    # Recurse into subdirectories
    for dir_path in dirs_to_recurse:
        await fetch_all_code_files(
            github_token, owner, repo, dir_path, collected, depth + 1, max_depth
        )

    return collected