"""
Rate Limiting Utilities
"""

from fastapi import HTTPException, Request
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, key: str, max_requests: int = 100, window: int = 3600) -> bool:
        """
        Check if request is allowed based on rate limit
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        
        # Clean up old requests periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(now, window)
            self.last_cleanup = now
        
        # Get requests for this key
        requests = self.requests[key]
        
        # Remove requests outside the window
        while requests and requests[0] <= now - window:
            requests.popleft()
        
        # Check if under limit
        if len(requests) >= max_requests:
            return False
        
        # Add current request
        requests.append(now)
        return True
    
    def _cleanup_old_requests(self, now: float, window: int):
        """Clean up old requests to prevent memory leaks"""
        cutoff = now - window
        keys_to_remove = []
        
        for key, requests in self.requests.items():
            while requests and requests[0] <= cutoff:
                requests.popleft()
            
            # Remove empty entries
            if not requests:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(request: Request, max_requests: int = 100, window: int = 3600):
    """
    FastAPI dependency to check rate limits
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_ip, max_requests, window):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True

def check_user_rate_limit(user_id: str, max_requests: int = 200, window: int = 3600):
    """
    Check rate limit for authenticated users (higher limits)
    
    Args:
        user_id: User ID
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    if not rate_limiter.is_allowed(f"user_{user_id}", max_requests, window):
        logger.warning(f"Rate limit exceeded for user: {user_id}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True

# Rate limit decorator for endpoints
def rate_limit(max_requests: int = 100, window: int = 3600):
    """
    Decorator for rate limiting endpoints
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs if available
            request = kwargs.get('request')
            if request:
                check_rate_limit(request, max_requests, window)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
