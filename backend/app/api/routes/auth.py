# backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime, timedelta

from ...core.config import settings
from ...core.security import create_access_token, get_github_oauth
from ...services.github_service import GitHubService
from ...models.schemas import TokenResponse, UserResponse
from ...db.session import get_db
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://github.com/login/oauth/authorize",
    tokenUrl="https://github.com/login/oauth/access_token",
)

@router.get("/github/url")
async def github_login():
    """Generate GitHub OAuth URL with state"""
    github_oauth = get_github_oauth()
    return {
        "url": github_oauth.get_authorize_url(),
        "state": github_oauth.state
    }

@router.post("/github/callback")
async def github_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        github_oauth = get_github_oauth()
        # Exchange code for access token
        token = await github_oauth.get_access_token(code)
        
        # Get user data from GitHub
        github_service = GitHubService(token)
        github_user = await github_service.get_user()
        
        # Find or create user in database
        user = db.query(User).filter(User.github_id == github_user["id"]).first()
        if not user:
            user = User(
                github_id=github_user["id"],
                username=github_user["login"],
                email=github_user.get("email"),
                avatar_url=github_user["avatar_url"],
                name=github_user.get("name")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "github_token": token}
        )
        
        # Set JWT token in HTTP-only cookie
        response = Response()
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to authenticate with GitHub: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Clear authentication cookie"""
    response = Response()
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get("/status")
async def check_auth_status(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Check current authentication status"""
    if not access_token:
        return {"isAuthenticated": False, "user": None}
    
    try:
        # Verify JWT token
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            return {"isAuthenticated": False, "user": None}
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return {"isAuthenticated": False, "user": None}
        
        return {
            "isAuthenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatarUrl": user.avatar_url,
                "name": user.name
            }
        }
    
    except jwt.PyJWTError:
        return {"isAuthenticated": False, "user": None}