"""
Health Check and System Monitoring
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database import get_db_context, engine
from models import Movie, User, Rating
import logging

logger = logging.getLogger(__name__)

# Health status thresholds
CPU_THRESHOLD = 80  # percent
MEMORY_THRESHOLD = 85  # percent
DISK_THRESHOLD = 90  # percent

class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time,
            "system": self._get_system_metrics(),
            "database": self._get_database_health(),
            "services": self._get_services_health()
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def _get_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            with get_db_context() as db:
                # Test basic connectivity
                db.execute("SELECT 1")
                
                # Get database stats
                movie_count = db.query(Movie).count()
                user_count = db.query(User).count()
                rating_count = db.query(Rating).count()
                
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "stats": {
                        "movies": movie_count,
                        "users": user_count,
                        "ratings": rating_count
                    }
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _get_services_health(self) -> Dict[str, Any]:
        """Check external services health"""
        services = {}
        
        # Check TMDB API (if configured)
        try:
            from services.tmdb_service import TMDBService
            tmdb = TMDBService()
            # Simple check - this would need to be async in real implementation
            services["tmdb"] = {
                "status": "configured",
                "api_key_set": bool(tmdb.api_key and tmdb.api_key != "your_tmdb_api_key_here")
            }
        except Exception as e:
            services["tmdb"] = {
                "status": "error",
                "error": str(e)
            }
        
        return services
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health information for debugging"""
        health = self.get_system_health()
        
        # Add additional debugging info
        health["debug"] = {
            "python_version": psutil.sys.version,
            "process_count": len(psutil.pids()),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        return health

# Global health checker instance
health_checker = HealthChecker()

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return health_checker.get_system_health()

def get_detailed_health() -> Dict[str, Any]:
    """Get detailed health status"""
    return health_checker.get_detailed_health()

def is_healthy() -> bool:
    """Check if system is healthy"""
    health = get_health_status()
    
    # Check if any critical component is unhealthy
    if health["database"]["status"] != "healthy":
        return False
    
    # Check system resources
    system = health["system"]
    if "error" not in system:
        if system["cpu_percent"] > 90:
            return False
        if system["memory"]["percent"] > 90:
            return False
        if system["disk"]["percent"] > 90:
            return False
    
    return True
