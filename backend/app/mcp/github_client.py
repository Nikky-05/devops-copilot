from functools import lru_cache

import requests
from langchain_core.tools import BaseTool, tool

from app.utils.config import get_settings

API = "https://api.github.com"


@lru_cache(maxsize=1)
def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = get_settings().github_token
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(path: str, params: dict | None = None):
    r = requests.get(f"{API}{path}", headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


@tool
def github_get_repo(owner_repo: str) -> dict:
    """Fetch metadata for a GitHub repository. `owner_repo` in 'owner/repo' format."""
    d = _get(f"/repos/{owner_repo}")
    return {
        "full_name": d["full_name"],
        "description": d.get("description"),
        "default_branch": d["default_branch"],
        "open_issues": d["open_issues_count"],
        "language": d.get("language"),
        "url": d["html_url"],
    }


@tool
def github_list_open_prs(owner_repo: str, limit: int = 10) -> list[dict]:
    """List open pull requests for a GitHub repository."""
    prs = _get(f"/repos/{owner_repo}/pulls", {"state": "open", "per_page": limit})
    return [
        {
            "number": p["number"],
            "title": p["title"],
            "user": p["user"]["login"],
            "url": p["html_url"],
        }
        for p in prs
    ]


@tool
def github_recent_workflow_runs(owner_repo: str, limit: int = 5) -> list[dict]:
    """List recent GitHub Actions workflow runs for a repository."""
    data = _get(f"/repos/{owner_repo}/actions/runs", {"per_page": limit})
    return [
        {
            "name": r.get("name"),
            "status": r["status"],
            "conclusion": r.get("conclusion"),
            "branch": r.get("head_branch"),
            "created_at": r["created_at"],
            "url": r["html_url"],
        }
        for r in data.get("workflow_runs", [])
    ]


def get_github_tools() -> list[BaseTool]:
    if not get_settings().github_token:
        return []
    return [github_get_repo, github_list_open_prs, github_recent_workflow_runs]
