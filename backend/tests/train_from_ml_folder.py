"""
Train ML Models from MovieLens 25M Dataset in ml/ folder
Loads data from ml/ml-25m/ and trains recommendation models
"""

import os
import sys
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Set testing flag to skip validation
os.environ['TESTING'] = 'true'

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import hashlib
import json

# Import database after env is loaded
from database.database import Base, engine, SessionLocal, get_db
from models import Movie, User, Rating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)


def get_db_context():
    """Get database context manager"""
    from contextlib import contextmanager
    
    @contextmanager
    def _get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return _get_db()


def load_dataset_from_ml_folder():
    """Load MovieLens 25M dataset from ml/ml-25m/ folder"""
    data_dir = Path("ml/ml-25m")
    
    if not data_dir.exists():
        logger.error(f"Dataset directory not found: {data_dir}")
        return None, None
    
    try:
        # Load movies (movieId,title,genres)
        logger.info("Loading movies from ml/ml-25m/movies.csv...")
        movies = pd.read_csv(data_dir / "movies.csv")
        logger.info(f"Loaded {len(movies)} movies")
        
        # Load ratings (userId,movieId,rating,timestamp)
        logger.info("Loading ratings from ml/ml-25m/ratings.csv...")
        logger.info("⚠️  This is a large file (678MB), please wait...")
        ratings = pd.read_csv(data_dir / "ratings.csv")
        logger.info(f"Loaded {len(ratings)} ratings")
        
        return movies, ratings
        
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        return None, None


def import_to_database(movies_df, ratings_df, limit_movies=2000, limit_ratings=50000):
    """
    Import MovieLens data to database
    
    Args:
        movies_df: Movies DataFrame
        ratings_df: Ratings DataFrame
        limit_movies: Maximum number of movies to import (default: 2000)
        limit_ratings: Maximum number of ratings to import (default: 50000)
    """
    try:
        init_db()
        
        with get_db_context() as db:
            # Import Movies
            logger.info(f"Importing movies (limit: {limit_movies})...")
            movies_added = 0
            movies_updated = 0
            
            for idx, row in movies_df.head(limit_movies).iterrows():
                try:
                    movie_id = int(row['movieId'])
                    title = row['title']
                    genres_str = row['genres']
                    
                    # Parse title and year
                    year = None
                    if '(' in title and ')' in title:
                        year_str = title[title.rfind('(')+1:title.rfind(')')]
                        if year_str.isdigit() and len(year_str) == 4:
                            year = year_str
                            title = title[:title.rfind('(')].strip()
                    
                    # Parse genres
                    genres_list = genres_str.split('|')
                    genres_json = json.dumps([{"name": g} for g in genres_list if g != '(no genres listed)'])
                    
                    # Check if movie exists
                    existing = db.query(Movie).filter(Movie.id == movie_id).first()
                    
                    if existing:
                        # Update existing movie
                        existing.title = title
                        existing.genres = genres_json
                        if year:
                            existing.release_date = f"{year}-01-01"
                        movies_updated += 1
                    else:
                        # Create new movie
                        movie = Movie(
                            id=movie_id,
                            title=title,
                            overview=f"A {genres_str.replace('|', ', ')} movie from MovieLens dataset",
                            release_date=f"{year}-01-01" if year else None,
                            genres=genres_json,
                            vote_average=0.0,
                            vote_count=0,
                            popularity=0.0
                        )
                        db.add(movie)
                        movies_added += 1
                    
                    if (movies_added + movies_updated) % 100 == 0:
                        db.commit()
                        logger.info(f"Progress: {movies_added} added, {movies_updated} updated...")
                        
                except Exception as e:
                    logger.error(f"Error importing movie {idx}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"✅ Movies import complete: {movies_added} added, {movies_updated} updated")
            
            # Get unique users from ratings
            logger.info("Extracting unique users from ratings...")
            unique_users = ratings_df['userId'].unique()
            logger.info(f"Found {len(unique_users)} unique users")
            
            # Import Users (create users for the ratings we'll import)
            logger.info("Creating user accounts...")
            users_added = 0
            
            # Sample users if too many
            if len(unique_users) > 1000:
                sampled_users = np.random.choice(unique_users, size=1000, replace=False)
            else:
                sampled_users = unique_users
            
            for user_id in sampled_users:
                try:
                    ml_user_id = f"ml_user_{user_id}"
                    existing = db.query(User).filter(User.id == ml_user_id).first()
                    
                    if existing:
                        continue
                    
                    user = User(
                        id=ml_user_id,
                        username=f"movielens_user_{user_id}",
                        email=f"user{user_id}@movielens.org",
                        password_hash=hashlib.sha256(f"password{user_id}".encode()).hexdigest(),
                        favorite_genres=json.dumps([])
                    )
                    
                    db.add(user)
                    users_added += 1
                    
                    if users_added % 100 == 0:
                        db.commit()
                        logger.info(f"Created {users_added} users...")
                        
                except Exception as e:
                    logger.error(f"Error creating user {user_id}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"✅ Users created: {users_added}")
            
            # Import Ratings
            logger.info(f"Importing ratings (limit: {limit_ratings})...")
            logger.info("Sampling ratings for faster import...")
            
            # Sample ratings intelligently
            if len(ratings_df) > limit_ratings:
                # Sample ratings that match our imported movies and users
                ratings_sample = ratings_df[
                    (ratings_df['movieId'].isin(movies_df.head(limit_movies)['movieId'])) &
                    (ratings_df['userId'].isin(sampled_users))
                ].sample(n=min(limit_ratings, len(ratings_df)), random_state=42)
            else:
                ratings_sample = ratings_df
            
            logger.info(f"Selected {len(ratings_sample)} ratings to import")
            
            ratings_added = 0
            ratings_skipped = 0
            
            for idx, row in ratings_sample.iterrows():
                try:
                    user_id = f"ml_user_{row['userId']}"
                    movie_id = int(row['movieId'])
                    rating_value = float(row['rating'])
                    timestamp = int(row['timestamp'])
                    
                    # Check if user and movie exist
                    user_exists = db.query(User).filter(User.id == user_id).first()
                    movie_exists = db.query(Movie).filter(Movie.id == movie_id).first()
                    
                    if not user_exists or not movie_exists:
                        ratings_skipped += 1
                        continue
                    
                    # Check if rating already exists
                    existing_rating = db.query(Rating).filter(
                        Rating.user_id == user_id,
                        Rating.movie_id == movie_id
                    ).first()
                    
                    if existing_rating:
                        ratings_skipped += 1
                        continue
                    
                    # Create rating
                    rating = Rating(
                        id=f"ml_rating_{user_id}_{movie_id}_{timestamp}",
                        user_id=user_id,
                        movie_id=movie_id,
                        rating=rating_value,
                        timestamp=datetime.fromtimestamp(timestamp)
                    )
                    
                    db.add(rating)
                    ratings_added += 1
                    
                    if ratings_added % 500 == 0:
                        db.commit()
                        logger.info(f"Imported {ratings_added} ratings (skipped {ratings_skipped})...")
                        
                except Exception as e:
                    logger.error(f"Error importing rating: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"✅ Ratings import complete: {ratings_added} added, {ratings_skipped} skipped")
            
            # Print summary
            logger.info("\n" + "="*60)
            logger.info("📊 IMPORT SUMMARY")
            logger.info("="*60)
            logger.info(f"Movies: {movies_added} added, {movies_updated} updated")
            logger.info(f"Users: {users_added} created")
            logger.info(f"Ratings: {ratings_added} imported")
            logger.info("="*60 + "\n")
            
            return True
            
    except Exception as e:
        logger.error(f"Error importing to database: {str(e)}")
        return False


def train_models():
    """Train ML models on imported data"""
    try:
        from ml.collaborative_filtering import CollaborativeFilteringModel
        
        logger.info("\n" + "="*60)
        logger.info("🤖 TRAINING ML MODELS")
        logger.info("="*60)
        
        with get_db_context() as db:
            # Get all ratings and movies
            logger.info("Loading data from database...")
            ratings = db.query(Rating).all()
            movies = db.query(Movie).all()
            
            if not ratings or not movies:
                logger.error("❌ No data found in database")
                return False
            
            logger.info(f"Found {len(ratings)} ratings and {len(movies)} movies")
            
            # Prepare data
            ratings_data = [
                {
                    "user_id": r.user_id,
                    "movie_id": r.movie_id,
                    "rating": float(r.rating)
                }
                for r in ratings
            ]
            
            movies_data = [
                {
                    "id": m.id,
                    "title": m.title,
                    "genres": m.genres
                }
                for m in movies
            ]
            
            # Initialize model
            logger.info("Initializing Collaborative Filtering model...")
            model = CollaborativeFilteringModel()
            
            # Prepare data
            logger.info("Preparing data...")
            if not model.prepare_data(ratings_data, movies_data):
                logger.error("❌ Failed to prepare data")
                return False
            
            # Compute user similarity
            logger.info("Computing user similarity matrix...")
            if not model.compute_user_similarity():
                logger.error("❌ Failed to compute user similarity")
                return False
            
            # Train SVD model
            logger.info("Training SVD model (Matrix Factorization)...")
            if not model.train_svd_model(n_components=50):
                logger.error("❌ Failed to train SVD model")
                return False
            
            # Train KNN model
            logger.info("Training KNN model...")
            if not model.train_knn_model(n_neighbors=20):
                logger.error("❌ Failed to train KNN model")
                return False
            
            # Save model
            model_dir = Path("models")
            model_dir.mkdir(exist_ok=True)
            model_path = model_dir / "collaborative_filtering_trained.pkl"
            
            logger.info(f"Saving model to {model_path}...")
            if model.save_model(str(model_path)):
                logger.info(f"✅ Model saved successfully!")
            else:
                logger.error("❌ Failed to save model")
                return False
            
            # Print results
            logger.info("\n" + "="*60)
            logger.info("✅ MODEL TRAINING COMPLETE!")
            logger.info("="*60)
            logger.info(f"Model saved to: {model_path}")
            logger.info(f"Training data: {len(ratings_data)} ratings, {len(movies_data)} movies")
            if model.rmse:
                logger.info(f"RMSE: {model.rmse:.4f}")
            if model.mae:
                logger.info(f"MAE: {model.mae:.4f}")
            logger.info("="*60 + "\n")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error training models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train models from ml/ml-25m/ dataset")
    parser.add_argument("--import", dest="import_data", action="store_true", help="Import data to database")
    parser.add_argument("--train", action="store_true", help="Train models")
    parser.add_argument("--all", action="store_true", help="Import and train")
    parser.add_argument("--limit-movies", type=int, default=500, help="Max movies to import (default: 500 for quick setup)")
    parser.add_argument("--limit-ratings", type=int, default=5000, help="Max ratings to import (default: 5000 for quick setup)")
    
    args = parser.parse_args()
    
    if args.all:
        args.import_data = True
        args.train = True
    
    if not (args.import_data or args.train):
        parser.print_help()
        exit(0)
    
    # Load dataset
    logger.info("="*60)
    logger.info("🎬 MOVIELENS 25M DATASET LOADER")
    logger.info("="*60)
    
    if args.import_data:
        logger.info("\n📂 Loading dataset from ml/ml-25m/...")
        movies_df, ratings_df = load_dataset_from_ml_folder()
        
        if movies_df is None or ratings_df is None:
            logger.error("❌ Failed to load dataset")
            exit(1)
        
        logger.info(f"\n📊 Dataset loaded:")
        logger.info(f"  - Movies: {len(movies_df):,}")
        logger.info(f"  - Ratings: {len(ratings_df):,}")
        
        logger.info(f"\n💾 Importing to database...")
        logger.info(f"  - Will import up to {args.limit_movies:,} movies")
        logger.info(f"  - Will import up to {args.limit_ratings:,} ratings")
        
        if not import_to_database(movies_df, ratings_df, args.limit_movies, args.limit_ratings):
            logger.error("❌ Import failed")
            exit(1)
    
    if args.train:
        if not train_models():
            logger.error("❌ Training failed")
            exit(1)
    
    logger.info("\n" + "="*60)
    logger.info("🎉 ALL OPERATIONS COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Start your backend: python main.py")
    logger.info("2. Test recommendations at: http://localhost:8000/docs")
    logger.info("="*60 + "\n")
