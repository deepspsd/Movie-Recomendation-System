"""
Test database connection and check existing data
"""

import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

os.environ['TESTING'] = 'true'

from database.database import Base, engine, SessionLocal
from models import Movie, User, Rating
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test database connection and check data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        
        # Get session
        db = SessionLocal()
        
        # Check existing data
        movie_count = db.query(Movie).count()
        user_count = db.query(User).count()
        rating_count = db.query(Rating).count()
        
        logger.info(f"📊 Current database state:")
        logger.info(f"  - Movies: {movie_count}")
        logger.info(f"  - Users: {user_count}")
        logger.info(f"  - Ratings: {rating_count}")
        
        if movie_count == 0:
            logger.info("📝 Database is empty, ready for import")
        else:
            logger.info("✅ Database contains data")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database()
