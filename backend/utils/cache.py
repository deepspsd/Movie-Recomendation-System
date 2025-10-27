"""
Caching Utilities for Movie Recommendation System
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if time.time() > entry['expires_at']:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)

# Global cache instance
cache = MemoryCache()

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    # Convert arguments to string and hash
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = 3600, key_func: Optional[callable] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom key generation function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key_str, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key_str, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def cache_movie_recommendations(user_id: str, algorithm: str = "hybrid") -> str:
    """Generate cache key for movie recommendations"""
    return f"recommendations:{user_id}:{algorithm}"

def cache_movie_details(movie_id: int) -> str:
    """Generate cache key for movie details"""
    return f"movie:{movie_id}"

def cache_search_results(query: str, filters: Dict[str, Any]) -> str:
    """Generate cache key for search results"""
    filter_str = json.dumps(filters, sort_keys=True)
    return f"search:{hashlib.md5((query + filter_str).encode()).hexdigest()}"

def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache entries for a user"""
    keys_to_remove = []
    for key in cache.cache.keys():
        if f":{user_id}:" in key or key.startswith(f"recommendations:{user_id}"):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        cache.delete(key)
    
    logger.info(f"Invalidated {len(keys_to_remove)} cache entries for user {user_id}")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    total_entries = len(cache.cache)
    expired_entries = cache.cleanup_expired()
    
    return {
        "total_entries": total_entries,
        "expired_entries_removed": expired_entries,
        "active_entries": total_entries - expired_entries
    }
