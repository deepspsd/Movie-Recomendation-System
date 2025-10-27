from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# Import custom middleware and error handlers
from utils.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware
)
from utils.error_handlers import register_error_handlers

# Load environment variables from project root
env_path = Path(__file__).parent.parent / '.env'
if not env_path.exists():
    # Try alternative path if running from different location
    env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Validate environment before starting (skip during testing)
from utils.env_validator import validate_environment
if not os.getenv('TESTING') and not validate_environment():
    print("[ERROR] Environment validation failed. Please check your .env file.")
    exit(1)

# Setup logging
from logging_config import setup_logging
logger = setup_logging()

# Import database and models
from database import init_db, close_db
from models import User, Movie, Rating, Watchlist, Review

# Import routes
from api.routes import auth, recommendations, movies, ratings, watchlist
from routes import omdb_routes

# Get configuration from environment
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173"]')

# Parse CORS origins
import json
try:
    cors_origins = json.loads(CORS_ORIGINS)
except:
    cors_origins = ["http://localhost:3000", "http://localhost:5173"]


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[INFO] Starting Movie Recommendation System API...")
    print("[INFO] Initializing database...")
    try:
        init_db()
        print("[OK] Database initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("[INFO] Shutting down...")
    close_db()
    print("[OK] Cleanup completed!")


# Create FastAPI application
app = FastAPI(
    title="Movie Recommendation System API",
    description="AI-powered movie recommendation system with personalized suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters!)
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=1.0)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Register error handlers
register_error_handlers(app)


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(movies.router, prefix="/api")
app.include_router(ratings.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(omdb_routes.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Movie Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from utils.health_check import get_health_status, is_healthy
    
    health_status = get_health_status()
    return {
        "status": "healthy" if is_healthy() else "unhealthy",
        "service": "Movie Recommendation System API",
        "version": "1.0.0",
        "details": health_status
    }

# Detailed health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint for debugging"""
    from utils.health_check import get_detailed_health
    
    return get_detailed_health()


# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Movie Recommendation System API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "movies": "/api/movies",
            "recommendations": "/api/recommendations",
            "ratings": "/api/ratings",
            "watchlist": "/api/watchlist"
        }
    }


# Run the application
if __name__ == "__main__":
    print(f"""
    ============================================================
    
         Movie Recommendation System API
    
         Server: http://{API_HOST}:{API_PORT}
         Docs: http://{API_HOST}:{API_PORT}/docs
         Health: http://{API_HOST}:{API_PORT}/health
    
    ============================================================
    """)
    
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )
