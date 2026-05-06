from fastapi import APIRouter, Request, Query
from services.repo_service import (
    list_user_repos,
    get_repo_tree,
    fetch_file_content,
    fetch_all_code_files,
)
from services.auth_service import get_user_by_id

router = APIRouter()


async def _get_github_token(request: Request) -> str:
    user_id = request.state.user_id
    user = await get_user_by_id(user_id)
    return user["github_token"]


@router.get("/")
async def list_repos(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    """List all repositories for the authenticated user."""
    github_token = await _get_github_token(request)
    repos = await list_user_repos(github_token, page=page, per_page=per_page)
    return {"repos": repos, "page": page, "per_page": per_page, "count": len(repos)}


@router.get("/{owner}/{repo}/tree")
async def get_tree(
    request: Request,
    owner: str,
    repo: str,
    path: str = Query("", description="Directory path within repo"),
):
    """Get file/directory tree of a repository."""
    github_token = await _get_github_token(request)
    tree = await get_repo_tree(github_token, owner, repo, path)
    return {"owner": owner, "repo": repo, "path": path, "tree": tree}


@router.get("/{owner}/{repo}/file")
async def get_file(
    request: Request,
    owner: str,
    repo: str,
    path: str = Query(..., description="File path within repo"),
):
    """Fetch content of a single file."""
    github_token = await _get_github_token(request)
    file_data = await fetch_file_content(github_token, owner, repo, path)
    return file_data


@router.get("/{owner}/{repo}/code")
async def get_all_code(
    request: Request,
    owner: str,
    repo: str,
):
    """
    Recursively fetch all code files in a repo.
    Returns structured data ready for LangChain ingestion.
    """
    github_token = await _get_github_token(request)
    files = await fetch_all_code_files(github_token, owner, repo)
    total_size = sum(f.get("size", 0) for f in files)
    return {
        "owner": owner,
        "repo": repo,
        "file_count": len(files),
        "total_size_bytes": total_size,
        "files": files,
    }