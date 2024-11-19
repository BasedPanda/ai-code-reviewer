# backend/app/services/analysis_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from ..models.schemas import (
    AnalyticsSummary,
    SuggestionType,
    ReviewStatus,
    SuggestionStatus
)
from ..models.schemas import (
    Analysis,
    Suggestion,
    PullRequest,
    Comment
)

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db

    async def create_analysis(
        self,
        pull_request_id: int,
        user_id: int
    ) -> Analysis:
        """Create a new analysis record"""
        analysis = Analysis(
            pull_request_id=pull_request_id,
            user_id=user_id,
            status=ReviewStatus.pending
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    async def update_analysis_status(
        self,
        analysis_id: int,
        status: ReviewStatus,
        error: Optional[str] = None
    ) -> Analysis:
        """Update analysis status"""
        analysis = self.db.query(Analysis).filter(
            Analysis.id == analysis_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        
        analysis.status = status
        analysis.error = error
        
        if status == ReviewStatus.completed:
            analysis.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    async def add_suggestions(
        self,
        analysis_id: int,
        suggestions: List[Dict[str, Any]]
    ) -> List[Suggestion]:
        """Add suggestions to an analysis"""
        analysis = self.db.query(Analysis).filter(
            Analysis.id == analysis_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        
        created_suggestions = []
        for suggestion_data in suggestions:
            suggestion = Suggestion(
                analysis_id=analysis_id,
                pull_request_id=analysis.pull_request_id,
                **suggestion_data
            )
            self.db.add(suggestion)
            created_suggestions.append(suggestion)
        
        self.db.commit()
        for suggestion in created_suggestions:
            self.db.refresh(suggestion)
        
        return created_suggestions

    async def get_analysis_summary(
        self,
        pull_request_id: int
    ) -> Dict[str, Any]:
        """Get summary of analysis results"""
        analysis = self.db.query(Analysis).filter(
            Analysis.pull_request_id == pull_request_id
        ).order_by(Analysis.created_at.desc()).first()
        
        if not analysis:
            return {
                "status": "not_found",
                "suggestions_count": 0,
                "suggestions_by_type": {},
                "suggestions_by_status": {}
            }
        
        suggestions = self.db.query(Suggestion).filter(
            Suggestion.analysis_id == analysis.id
        ).all()
        
        suggestions_by_type = {}
        suggestions_by_status = {}
        
        for suggestion in suggestions:
            suggestions_by_type[suggestion.type] = suggestions_by_type.get(
                suggestion.type, 0
            ) + 1
            suggestions_by_status[suggestion.status] = suggestions_by_status.get(
                suggestion.status, 0
            ) + 1
        
        return {
            "status": analysis.status,
            "suggestions_count": len(suggestions),
            "suggestions_by_type": suggestions_by_type,
            "suggestions_by_status": suggestions_by_status,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at
        }

    def get_user_analytics(self, user_id: int) -> AnalyticsSummary:
        """Get analytics summary for a user"""
        # Get base query for user's analyses
        base_query = self.db.query(Analysis).filter(
            Analysis.user_id == user_id,
            Analysis.status == ReviewStatus.completed
        )
        
        # Calculate total reviews
        total_reviews = base_query.count()
        
        # Calculate average time to review
        completed_analyses = base_query.filter(
            Analysis.completed_at.isnot(None)
        ).all()
        
        if completed_analyses:
            total_time = sum(
                (a.completed_at - a.created_at).total_seconds()
                for a in completed_analyses
            )
            avg_time = total_time / len(completed_analyses) / 60  # Convert to minutes
        else:
            avg_time = 0
        
        # Get suggestion statistics
        suggestions = self.db.query(Suggestion).filter(
            Suggestion.analysis_id.in_(
                base_query.with_entities(Analysis.id)
            )
        ).all()
        
        suggestions_by_type = {
            suggestion_type: 0
            for suggestion_type in SuggestionType
        }
        
        suggestions_accepted = 0
        for suggestion in suggestions:
            suggestions_by_type[suggestion.type] += 1
            if suggestion.status == SuggestionStatus.accepted:
                suggestions_accepted += 1
        
        # Get recent activity
        recent_activity = []
        for days_ago in range(7):
            date = datetime.utcnow().date() - timedelta(days=days_ago)
            
            daily_stats = {
                "date": date.isoformat(),
                "reviews": base_query.filter(
                    func.date(Analysis.created_at) == date
                ).count(),
                "suggestions": self.db.query(Suggestion).filter(
                    func.date(Suggestion.created_at) == date
                ).count()
            }
            
            recent_activity.append(daily_stats)
        
        # Get top issues
        top_issues = self.db.query(
            Suggestion.type,
            func.count(Suggestion.id).label('count')
        ).group_by(
            Suggestion.type
        ).order_by(
            func.count(Suggestion.id).desc()
        ).limit(5).all()
        
        return AnalyticsSummary(
            total_reviews=total_reviews,
            average_time_to_review=avg_time,
            suggestions_generated=len(suggestions),
            suggestions_accepted=suggestions_accepted,
            suggestions_by_type=suggestions_by_type,
            top_issues=[{
                "type": issue_type,
                "count": count,
                "examples": self._get_issue_examples(issue_type)
            } for issue_type, count in top_issues],
            recent_activity=recent_activity
        )

    def _get_issue_examples(
        self,
        issue_type: str,
        limit: int = 3
    ) -> List[str]:
        """Get example messages for an issue type"""
        examples = self.db.query(
            Suggestion.message
        ).filter(
            Suggestion.type == issue_type
        ).order_by(
            func.random()
        ).limit(limit).all()
        
        return [example[0] for example in examples]