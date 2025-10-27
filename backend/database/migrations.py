"""
Database Migration Helper
Creates indexes for better query performance
"""

from sqlalchemy import text
from database import engine, get_db_context
import logging

logger = logging.getLogger(__name__)


def create_performance_indexes():
    """Create indexes for frequently queried columns"""
    
    indexes = [
        # Movie indexes
        "CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average DESC)",
        "CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity DESC)",
        "CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date DESC)",
        
        # Rating indexes (already have user_id and movie_id from model)
        "CREATE INDEX IF NOT EXISTS idx_ratings_rating ON ratings(rating DESC)",
        "CREATE INDEX IF NOT EXISTS idx_ratings_timestamp ON ratings(timestamp DESC)",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_ratings_user_timestamp ON ratings(user_id, timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_watchlist_user_added ON watchlist(user_id, added_at DESC)",
    ]
    
    try:
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                    logger.info(f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    logger.warning(f"Index creation skipped (may already exist): {str(e)}")
        
        logger.info("✅ All performance indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {str(e)}")
        return False


def optimize_database():
    """Run database optimization commands"""
    
    optimization_commands = [
        "ANALYZE TABLE movies",
        "ANALYZE TABLE ratings",
        "ANALYZE TABLE users",
        "ANALYZE TABLE watchlist",
    ]
    
    try:
        with engine.connect() as conn:
            for cmd in optimization_commands:
                try:
                    conn.execute(text(cmd))
                    conn.commit()
                    logger.info(f"Optimized: {cmd}")
                except Exception as e:
                    logger.warning(f"Optimization skipped: {str(e)}")
        
        logger.info("✅ Database optimization completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error optimizing database: {str(e)}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Creating performance indexes...")
    create_performance_indexes()
    print("\nOptimizing database...")
    optimize_database()
    print("\n✅ Database optimization complete!")
