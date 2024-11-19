# backend/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .core.security import setup_cors
from .db.session import SessionLocal, engine, Base
from .api.routes import auth, github, analysis, websocket
from .services.github_service import GitHubService
from .services.llm_service import LLMService
from .services.analysis_service import AnalysisService

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Creates database tables on startup.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down application...")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered code review assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS
setup_cors(app)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Include routers
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["authentication"]
)

app.include_router(
    github.router,
    prefix=settings.API_V1_STR,
    tags=["github"],
    dependencies=[Depends(get_db)]
)

app.include_router(
    analysis.router,
    prefix=settings.API_V1_STR,
    tags=["analysis"],
    dependencies=[Depends(get_db)]
)

app.include_router(
    websocket.router,
    prefix=settings.API_V1_STR,
    tags=["websocket"]
)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
    }

# WebSocket connection manager
from .api.routes.websocket import manager

@app.on_event("startup")
async def startup_event():
    """
    Initialize services and connections on startup
    """
    logger.info("Initializing application services...")
    
    # Initialize WebSocket manager
    app.state.ws_manager = manager
    
    # Initialize services (if needed)
    app.state.llm_service = LLMService()
    
    logger.info("Application services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info("Shutting down application services...")
    
    # Close any open WebSocket connections
    for connection in app.state.ws_manager.active_connections.values():
        await connection.close()
    
    logger.info("Application shutdown complete")

# Development server configuration
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.MAX_WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )