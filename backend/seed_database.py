"""
Database Seeding Script
Populates database with real movie data from TMDB API
"""

import asyncio
import logging
from sqlalchemy.orm import Session
from database import get_db_context, init_db
from models import Movie, User, Rating
from services.tmdb_service import get_tmdb_movies_data, get_tmdb_movie_details
import json
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_movies(db: Session, limit: int = 200):
    """Seed database with movies from TMDB"""
    try:
        logger.info("Starting movie seeding from TMDB...")
        
        # Get movies from TMDB
        tmdb_movies = await get_tmdb_movies_data(limit)
        
        if not tmdb_movies:
            logger.error("No movies retrieved from TMDB")
            return False
        
        movies_added = 0
        movies_updated = 0
        
        for movie_data in tmdb_movies:
            try:
                # Check if movie already exists
                existing_movie = db.query(Movie).filter(Movie.id == movie_data["id"]).first()
                
                if existing_movie:
                    # Update existing movie
                    existing_movie.title = movie_data["title"]
                    existing_movie.overview = movie_data["overview"]
                    existing_movie.poster_path = movie_data["poster_path"]
                    existing_movie.backdrop_path = movie_data["backdrop_path"]
                    existing_movie.release_date = movie_data["release_date"]
                    existing_movie.vote_average = movie_data["vote_average"]
                    existing_movie.vote_count = movie_data["vote_count"]
                    existing_movie.popularity = movie_data["popularity"]
                    existing_movie.genres = json.dumps(movie_data["genres"])
                    existing_movie.updated_at = datetime.utcnow()
                    movies_updated += 1
                else:
                    # Create new movie
                    new_movie = Movie(
                        id=movie_data["id"],
                        title=movie_data["title"],
                        overview=movie_data["overview"],
                        poster_path=movie_data["poster_path"],
                        backdrop_path=movie_data["backdrop_path"],
                        release_date=movie_data["release_date"],
                        vote_average=movie_data["vote_average"],
                        vote_count=movie_data["vote_count"],
                        popularity=movie_data["popularity"],
                        genres=json.dumps(movie_data["genres"])
                    )
                    db.add(new_movie)
                    movies_added += 1
                    
            except Exception as e:
                logger.error(f"Error processing movie {movie_data.get('id', 'unknown')}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Movie seeding completed: {movies_added} added, {movies_updated} updated")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding movies: {str(e)}")
        db.rollback()
        return False


def create_demo_users(db: Session):
    """Create demo users for testing"""
    try:
        logger.info("Creating demo users...")
        
        demo_users = [
            {
                "id": "demo_user_1",
                "username": "movie_lover_1",
                "email": "user1@demo.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J7J8Q8Q8Q",  # "password123"
                "favorite_genres": json.dumps(["Action", "Comedy", "Drama"])
            },
            {
                "id": "demo_user_2", 
                "username": "cinema_fan_2",
                "email": "user2@demo.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J7J8Q8Q8Q",  # "password123"
                "favorite_genres": json.dumps(["Horror", "Thriller", "Sci-Fi"])
            },
            {
                "id": "demo_user_3",
                "username": "film_critic_3", 
                "email": "user3@demo.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J7J8Q8Q8Q",  # "password123"
                "favorite_genres": json.dumps(["Romance", "Comedy", "Animation"])
            }
        ]
        
        users_created = 0
        for user_data in demo_users:
            existing_user = db.query(User).filter(User.id == user_data["id"]).first()
            if not existing_user:
                new_user = User(**user_data)
                db.add(new_user)
                users_created += 1
        
        db.commit()
        logger.info(f"Created {users_created} demo users")
        return True
        
    except Exception as e:
        logger.error(f"Error creating demo users: {str(e)}")
        db.rollback()
        return False


def create_demo_ratings(db: Session):
    """Create demo ratings for testing recommendations"""
    try:
        logger.info("Creating demo ratings...")
        
        # Get all movies and users
        movies = db.query(Movie).all()
        users = db.query(User).all()
        
        if not movies or not users:
            logger.warning("No movies or users found for rating creation")
            return False
        
        ratings_created = 0
        
        for user in users:
            # Each user rates 20-50 random movies
            num_ratings = random.randint(20, 50)
            user_movies = random.sample(movies, min(num_ratings, len(movies)))
            
            for movie in user_movies:
                # Check if rating already exists
                existing_rating = db.query(Rating).filter(
                    Rating.user_id == user.id,
                    Rating.movie_id == movie.id
                ).first()
                
                if not existing_rating:
                    # Generate realistic rating based on movie quality
                    base_rating = movie.vote_average or 5.0
                    # Add some personal variation
                    personal_variation = random.uniform(-1.5, 1.5)
                    rating_value = max(1.0, min(5.0, base_rating + personal_variation))
                    
                    # Round to nearest 0.5
                    rating_value = round(rating_value * 2) / 2
                    
                    new_rating = Rating(
                        id=f"rating_{user.id}_{movie.id}",
                        user_id=user.id,
                        movie_id=movie.id,
                        rating=rating_value,
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 365))
                    )
                    db.add(new_rating)
                    ratings_created += 1
        
        db.commit()
        logger.info(f"Created {ratings_created} demo ratings")
        return True
        
    except Exception as e:
        logger.error(f"Error creating demo ratings: {str(e)}")
        db.rollback()
        return False


async def seed_database():
    """Main seeding function"""
    try:
        logger.info("Starting database seeding...")
        
        # Initialize database
        init_db()
        
        with get_db_context() as db:
            # Seed movies from TMDB
            movies_success = await seed_movies(db, limit=300)
            if not movies_success:
                logger.error("Movie seeding failed")
                return False
            
            # Create demo users
            users_success = create_demo_users(db)
            if not users_success:
                logger.error("User creation failed")
                return False
            
            # Create demo ratings
            ratings_success = create_demo_ratings(db)
            if not ratings_success:
                logger.error("Rating creation failed")
                return False
            
            logger.info("Database seeding completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error in database seeding: {str(e)}")
        return False


if __name__ == "__main__":
    # Run the seeding
    asyncio.run(seed_database())
