# backend/app/services/github_service.py

from typing import List, Dict, Any, Optional
import aiohttp
from fastapi import HTTPException

class GitHubService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Any:
        """Make a request to GitHub API"""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data
            ) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise HTTPException(
                        status_code=response.status,
                        detail=error_data.get("message", "GitHub API error")
                    )
                return await response.json()

    async def get_user(self) -> Dict[str, Any]:
        """Get authenticated user details"""
        return await self._make_request("GET", "/user")

    async def list_repositories(
        self,
        sort: str = "updated",
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """List repositories accessible to the authenticated user"""
        return await self._make_request(
            "GET",
            f"/user/repos?sort={sort}&direction={direction}"
        )

    async def list_pull_requests(
        self,
        repo: str,
        state: str = "open"
    ) -> List[Dict[str, Any]]:
        """List pull requests for a repository"""
        return await self._make_request(
            "GET",
            f"/repos/{repo}/pulls?state={state}"
        )

    async def get_pull_request(
        self,
        repo: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """Get detailed information about a specific pull request"""
        return await self._make_request(
            "GET",
            f"/repos/{repo}/pulls/{pr_number}"
        )

    async def get_pull_request_files(
        self,
        repo: str,
        pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        return await self._make_request(
            "GET",
            f"/repos/{repo}/pulls/{pr_number}/files"
        )

    async def get_file_content(
        self,
        repo: str,
        path: str,
        ref: str
    ) -> str:
        """Get content of a file"""
        response = await self._make_request(
            "GET",
            f"/repos/{repo}/contents/{path}?ref={ref}"
        )
        import base64
        return base64.b64decode(response["content"]).decode()

    async def create_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int
    ) -> Dict[str, Any]:
        """Create a review comment on a pull request"""
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "side": "RIGHT"
        }
        return await self._make_request(
            "POST",
            f"/repos/{repo}/pulls/{pr_number}/comments",
            data
        )

    async def create_review(
        self,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: List[Dict] = None
    ) -> Dict[str, Any]:
        """Create a review on a pull request"""
        data = {
            "body": body,
            "event": event,
            "comments": comments or []
        }
        return await self._make_request(
            "POST",
            f"/repos/{repo}/pulls/{pr_number}/reviews",
            data
        )

    async def update_pull_request(
        self,
        repo: str,
        pr_number: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a pull request"""
        return await self._make_request(
            "PATCH",
            f"/repos/{repo}/pulls/{pr_number}",
            data
        )

    async def get_commit(
        self,
        repo: str,
        commit_sha: str
    ) -> Dict[str, Any]:
        """Get a specific commit"""
        return await self._make_request(
            "GET",
            f"/repos/{repo}/commits/{commit_sha}"
        )