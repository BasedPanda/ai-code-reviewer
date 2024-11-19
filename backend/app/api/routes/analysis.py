# backend/app/api/routes/analysis.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ...core.security import get_current_user
from ...services.analysis_service import AnalysisService
from ...services.github_service import GitHubService
from ...services.llm_service import LLMService
from ...db.session import get_db
from ...models.schemas import (
    CodeSuggestion,
    AnalysisResponse,
    AnalyticsSummary,
    SuggestionUpdate
)
from ...models.analysis import Analysis, Suggestion

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/pull-requests/{pr_id}/analyze")
async def analyze_pull_request(
    pr_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start analysis of a pull request"""
    try:
        # Check if analysis is already in progress
        existing_analysis = db.query(Analysis).filter(
            Analysis.pull_request_id == pr_id,
            Analysis.status == "in_progress"
        ).first()
        
        if existing_analysis:
            return {
                "message": "Analysis already in progress",
                "analysis_id": existing_analysis.id
            }
        
        # Create new analysis record
        analysis = Analysis(
            pull_request_id=pr_id,
            user_id=current_user.id,
            status="pending"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Start analysis in background
        background_tasks.add_task(
            analyze_pr_background,
            pr_id,
            analysis.id,
            current_user.github_token,
            db
        )
        
        return {
            "message": "Analysis started",
            "analysis_id": analysis.id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )

@router.get("/pull-requests/{pr_id}/status", response_model=AnalysisResponse)
async def get_analysis_status(
    pr_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of pull request analysis"""
    analysis = db.query(Analysis).filter(
        Analysis.pull_request_id == pr_id
    ).order_by(Analysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this pull request"
        )
    
    return {
        "id": analysis.id,
        "status": analysis.status,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at,
        "error": analysis.error
    }

@router.get("/pull-requests/{pr_id}/suggestions", response_model=List[CodeSuggestion])
async def get_suggestions(
    pr_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all suggestions for a pull request"""
    suggestions = db.query(Suggestion).filter(
        Suggestion.pull_request_id == pr_id
    ).all()
    
    return suggestions

@router.put("/suggestions/{suggestion_id}", response_model=CodeSuggestion)
async def update_suggestion(
    suggestion_id: int,
    update: SuggestionUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the status of a suggestion"""
    suggestion = db.query(Suggestion).filter(
        Suggestion.id == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found"
        )
    
    suggestion.status = update.status
    db.commit()
    db.refresh(suggestion)
    
    return suggestion

@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics summary for the authenticated user"""
    analysis_service = AnalysisService(db)
    analytics = analysis_service.get_user_analytics(current_user.id)
    return analytics

async def analyze_pr_background(
    pr_id: int,
    analysis_id: int,
    github_token: str,
    db: Session
):
    """Background task for analyzing pull request"""
    try:
        # Update analysis status
        analysis = db.query(Analysis).get(analysis_id)
        analysis.status = "in_progress"
        db.commit()
        
        # Initialize services
        github_service = GitHubService(github_token)
        llm_service = LLMService()
        
        # Get PR files
        files = await github_service.get_pull_request_files(pr_id)
        
        # Analyze each file
        for file in files:
            # Skip binary files, large files, etc.
            if not should_analyze_file(file):
                continue
                
            # Get file content
            content = await github_service.get_file_content(
                file["raw_url"]
            )
            
            # Analyze code with LLM
            suggestions = await llm_service.analyze_code(
                content,
                file["filename"],
                file["patch"]
            )
            
            # Store suggestions in database
            for suggestion in suggestions:
                new_suggestion = Suggestion(
                    analysis_id=analysis_id,
                    pull_request_id=pr_id,
                    file_path=file["filename"],
                    line_start=suggestion["line_start"],
                    line_end=suggestion["line_end"],
                    type=suggestion["type"],
                    message=suggestion["message"],
                    original_code=suggestion["original_code"],
                    suggested_code=suggestion["suggested_code"],
                    explanation=suggestion["explanation"],
                    confidence=suggestion["confidence"]
                )
                db.add(new_suggestion)
            
            db.commit()
        
        # Update analysis status to completed
        analysis.status = "completed"
        analysis.completed_at = datetime.utcnow()
        db.commit()
        
        # Notify clients through WebSocket
        await notify_analysis_complete(analysis_id, pr_id)
        
    except Exception as e:
        # Update analysis status to failed
        analysis = db.query(Analysis).get(analysis_id)
        analysis.status = "failed"
        analysis.error = str(e)
        db.commit()
        
        # Notify clients through WebSocket
        await notify_analysis_error(analysis_id, pr_id, str(e))
        
def should_analyze_file(file: dict) -> bool:
    """Determine if a file should be analyzed"""
    # Skip binary files
    if file.get("status") == "removed" or file.get("binary"):
        return False
    
    # Skip files that are too large
    if file.get("changes", 0) > 1000:
        return False
    
    # Skip certain file types
    ignored_extensions = {
        '.min.js', '.min.css', '.lock', '.map',
        '.jpg', '.png', '.gif', '.svg', '.ico',
        '.pdf', '.doc', '.docx', '.zip'
    }
    
    file_name = file.get("filename", "").lower()
    return not any(file_name.endswith(ext) for ext in ignored_extensions)