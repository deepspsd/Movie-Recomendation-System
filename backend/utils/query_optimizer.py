"""
Database Query Optimization Utilities
Helpers for efficient database queries
"""

from sqlalchemy.orm import Query, joinedload, selectinload
from typing import List, Type, Any
from models import Movie, Rating, User, Watchlist
import logging

logger = logging.getLogger(__name__)


def optimize_movie_query(query: Query) -> Query:
    """
    Optimize movie queries with common joins and filters
    """
    # Add eager loading for commonly accessed relationships
    return query.options(
        selectinload(Movie.ratings) if hasattr(Movie, 'ratings') else None
    ).filter(Movie.vote_count > 0)


def get_top_rated_movies(db, limit: int = 20, min_votes: int = 100):
    """
    Get top rated movies with optimized query
    """
    return db.query(Movie).filter(
        Movie.vote_count >= min_votes,
        Movie.vote_average >= 7.0
    ).order_by(
        Movie.vote_average.desc(),
        Movie.vote_count.desc()
    ).limit(limit).all()


def get_trending_movies(db, limit: int = 20):
    """
    Get trending movies based on popularity and recent ratings
    """
    return db.query(Movie).filter(
        Movie.popularity > 10
    ).order_by(
        Movie.popularity.desc()
    ).limit(limit).all()


def get_user_recommendations_optimized(db, user_id: str, limit: int = 10):
    """
    Get user recommendations with optimized queries
    Uses subqueries to reduce database round trips
    """
    from sqlalchemy import func, and_
    
    # Get user's rated movies
    user_ratings = db.query(Rating.movie_id).filter(
        Rating.user_id == user_id
    ).subquery()
    
    # Get movies user hasn't rated, sorted by popularity
    recommendations = db.query(Movie).filter(
        ~Movie.id.in_(user_ratings),
        Movie.vote_average >= 6.5,
        Movie.vote_count >= 50
    ).order_by(
        Movie.popularity.desc()
    ).limit(limit).all()
    
    return recommendations


def batch_get_movies(db, movie_ids: List[int]):
    """
    Efficiently fetch multiple movies by ID
    """
    return db.query(Movie).filter(
        Movie.id.in_(movie_ids)
    ).all()


def get_user_stats(db, user_id: str):
    """
    Get user statistics with a single optimized query
    """
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Rating.id).label('total_ratings'),
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Watchlist.id).label('watchlist_count')
    ).outerjoin(
        Rating, Rating.user_id == user_id
    ).outerjoin(
        Watchlist, Watchlist.user_id == user_id
    ).first()
    
    return {
        'total_ratings': stats.total_ratings or 0,
        'average_rating': round(float(stats.avg_rating or 0), 2),
        'watchlist_count': stats.watchlist_count or 0
    }


class QueryCache:
    """Simple query result cache"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get(self, key: str):
        """Get cached result"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache a result"""
        if len(self.cache) >= self.max_size:
            # Remove least accessed item
            least_used = min(self.access_count.items(), key=lambda x: x[1])[0]
            del self.cache[least_used]
            del self.access_count[least_used]
        
        self.cache[key] = value
        self.access_count[key] = 0
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_count.clear()


# Global query cache
query_cache = QueryCache()
