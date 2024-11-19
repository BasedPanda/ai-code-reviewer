# backend/app/models/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class PullRequestStatus(str, Enum):
    open = "open"
    closed = "closed"
    merged = "merged"

class ReviewStatus(str, Enum):
    pending = "pending"
    reviewing = "reviewing"
    completed = "completed"
    failed = "failed"

class SuggestionType(str, Enum):
    improvement = "improvement"
    security = "security"
    performance = "performance"
    style = "style"

class SuggestionStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

# Base Models
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    name: Optional[str] = None

class UserCreate(UserBase):
    github_id: int

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Repository Models
class RepositoryBase(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool = False
    default_branch: str = "main"

class RepositoryResponse(RepositoryBase):
    id: int
    url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pull Request Models
class PullRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    base_branch: str
    head_branch: str

class PullRequestCreate(PullRequestBase):
    repository_id: int

class PullRequestResponse(PullRequestBase):
    id: int
    number: int
    status: PullRequestStatus
    review_status: ReviewStatus
    author: UserResponse
    repository: RepositoryResponse
    created_at: datetime
    updated_at: datetime
    total_comments: int
    total_suggestions: int

    class Config:
        from_attributes = True

# Analysis Models
class AnalysisBase(BaseModel):
    pull_request_id: int
    status: ReviewStatus
    error: Optional[str] = None

class AnalysisCreate(AnalysisBase):
    user_id: int

class AnalysisResponse(AnalysisBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Suggestion Models
class SuggestionBase(BaseModel):
    type: SuggestionType
    message: str
    file_path: str
    line_start: int
    line_end: int
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class SuggestionCreate(SuggestionBase):
    analysis_id: int
    pull_request_id: int

class SuggestionResponse(SuggestionBase):
    id: int
    status: SuggestionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SuggestionUpdate(BaseModel):
    status: SuggestionStatus

# Comment Models
class CommentBase(BaseModel):
    content: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class CommentCreate(CommentBase):
    pull_request_id: int
    user_id: int

class CommentResponse(CommentBase):
    id: int
    author: UserResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics Models
class AnalyticsSummary(BaseModel):
    total_reviews: int
    average_time_to_review: float
    suggestions_generated: int
    suggestions_accepted: int
    suggestions_by_type: Dict[SuggestionType, int]
    top_issues: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]

# WebSocket Models
class WebSocketMessage(BaseModel):
    type: str
    payload: Dict[str, Any]

# Database Models (SQLAlchemy)
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime,
    Boolean, Float, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    avatar_url = Column(String)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    pull_requests = relationship("PullRequest", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    full_name = Column(String, unique=True, index=True)
    description = Column(Text)
    private = Column(Boolean, default=False)
    default_branch = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    pull_requests = relationship("PullRequest", back_populates="repository")

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    title = Column(String)
    description = Column(Text)
    status = Column(SQLEnum(PullRequestStatus))
    review_status = Column(SQLEnum(ReviewStatus))
    base_branch = Column(String)
    head_branch = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="pull_requests")
    repository = relationship("Repository", back_populates="pull_requests")
    analyses = relationship("Analysis", back_populates="pull_request")
    suggestions = relationship("Suggestion", back_populates="pull_request")
    comments = relationship("Comment", back_populates="pull_request")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ReviewStatus))
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    pull_request = relationship("PullRequest", back_populates="analyses")
    suggestions = relationship("Suggestion", back_populates="analysis")

class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    type = Column(SQLEnum(SuggestionType))
    status = Column(SQLEnum(SuggestionStatus), default=SuggestionStatus.pending)
    message = Column(Text)
    file_path = Column(String)
    line_start = Column(Integer)
    line_end = Column(Integer)
    original_code = Column(Text)
    suggested_code = Column(Text)
    explanation = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    analysis = relationship("Analysis", back_populates="suggestions")
    pull_request = relationship("PullRequest", back_populates="suggestions")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    file_path = Column(String)
    line_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="comments")
    pull_request = relationship("PullRequest", back_populates="comments")