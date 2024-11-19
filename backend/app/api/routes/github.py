# backend/app/api/routes/github.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.security import get_current_user
from ...services.github_service import GitHubService
from ...db.session import get_db
from ...models.schemas import (
    PullRequestResponse,
    PullRequestDetailResponse,
    RepositoryResponse,
    CommentCreate,
    CommentResponse
)

router = APIRouter(prefix="/github", tags=["github"])

@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List repositories accessible to the authenticated user"""
    try:
        github_service = GitHubService(current_user.github_token)
        repos = await github_service.list_repositories()
        return repos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch repositories: {str(e)}"
        )

@router.get("/pull-requests", response_model=List[PullRequestResponse])
async def list_pull_requests(
    repository: str = None,
    state: str = "open",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List pull requests, optionally filtered by repository"""
    try:
        github_service = GitHubService(current_user.github_token)
        pull_requests = await github_service.list_pull_requests(repository, state)
        return pull_requests
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pull requests: {str(e)}"
        )

@router.get("/pull-requests/{pr_id}", response_model=PullRequestDetailResponse)
async def get_pull_request(
    pr_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific pull request"""
    try:
        github_service = GitHubService(current_user.github_token)
        pr_detail = await github_service.get_pull_request(pr_id)
        return pr_detail
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pull request details: {str(e)}"
        )

@router.get("/pull-requests/{pr_id}/files")
async def get_pull_request_files(
    pr_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files changed in a pull request"""
    try:
        github_service = GitHubService(current_user.github_token)
        files = await github_service.get_pull_request_files(pr_id)
        return files
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pull request files: {str(e)}"
        )

@router.post("/pull-requests/{pr_id}/comments", response_model=CommentResponse)
async def create_comment(
    pr_id: int,
    comment: CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on a pull request"""
    try:
        github_service = GitHubService(current_user.github_token)
        new_comment = await github_service.create_comment(
            pr_id,
            comment.content,
            comment.path,
            comment.line
        )
        return new_comment
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create comment: {str(e)}"
        )

@router.get("/pull-requests/{pr_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    pr_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all comments on a pull request"""
    try:
        github_service = GitHubService(current_user.github_token)
        comments = await github_service.list_comments(pr_id)
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch comments: {str(e)}"
        )

@router.post("/pull-requests/{pr_id}/reviews")
async def create_review(
    pr_id: int,
    body: str,
    event: str = "COMMENT",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review on a pull request"""
    try:
        github_service = GitHubService(current_user.github_token)
        review = await github_service.create_review(pr_id, body, event)
        return review
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create review: {str(e)}"
        )