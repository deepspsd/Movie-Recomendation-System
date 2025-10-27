#!/usr/bin/env python3
"""
Production startup script for Movie Recommendation System
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from logging_config import setup_logging

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME',
        'SECRET_KEY', 'JWT_SECRET_KEY', 'TMDB_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    return True

def check_database_connection():
    """Check database connectivity"""
    try:
        from database import get_db_context
        with get_db_context() as db:
            db.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    logger = setup_logging()
    logger.info("Starting Movie Recommendation System in production mode")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check database
    if not check_database_connection():
        sys.exit(1)
    
    # Start the application
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            workers=4,  # Adjust based on your server
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_application()
