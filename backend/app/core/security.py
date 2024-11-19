# backend/app/core/security.py

from datetime import datetime, timedelta
from typing import Any, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import secrets
from aiohttp import ClientSession
from urllib.parse import urlencode

from .config import settings
from ..db.session import get_db
from ..models.user import User

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://github.com/login/oauth/authorize",
    tokenUrl="https://github.com/login/oauth/access_token",
)

class GitHubOAuth:
    def __init__(self):
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.callback_url = settings.GITHUB_CALLBACK_URL
        self.state = secrets.token_urlsafe(32)
    
    def get_authorize_url(self) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': 'repo user',
            'state': self.state
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    async def get_access_token(self, code: str) -> str:
        """Exchange code for access token"""
        async with ClientSession() as session:
            async with session.post(
                'https://github.com/login/oauth/access_token',
                json={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': self.callback_url
                },
                headers={'Accept': 'application/json'}
            ) as response:
                data = await response.json()
                if 'error' in data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"GitHub OAuth error: {data['error_description']}"
                    )
                return data['access_token']

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_ws(token: str) -> User:
    """Get current user from WebSocket connection"""
    try:
        payload = verify_token(token)
        db = next(get_db())
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        return user
    except Exception:
        return None

def get_github_oauth() -> GitHubOAuth:
    """Get GitHub OAuth instance"""
    return GitHubOAuth()

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests = {
            k: v for k, v in self.requests.items()
            if v > window_start
        }
        
        # Check current requests
        user_requests = [
            t for t in self.requests.get(key, [])
            if t > window_start
        ]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        # Add new request
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append(now)
        
        return True

# Password hashing (for potential future use)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: Any) -> None:
    """Setup CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize rate limiter
rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE
)