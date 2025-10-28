"""
Load MovieLens Dataset and Train ML Models
Downloads and processes MovieLens 1M dataset for recommendation system
"""

import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from database import get_db_context, init_db
from models import Movie, User, Rating
import logging
from datetime import datetime
import hashlib
import json
import requests
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_movielens_dataset(dataset_size="1m"):
    """
    Download MovieLens dataset
    
    Args:
        dataset_size: "1m" for 1 million ratings, "25m" for 25 million ratings
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    urls = {
        "1m": "https://files.grouplens.org/datasets/movielens/ml-1m.zip",
        "25m": "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
    }
    
    if dataset_size not in urls:
        logger.error(f"Invalid dataset size: {dataset_size}")
        return False
    
    url = urls[dataset_size]
    zip_path = data_dir / f"ml-{dataset_size}.zip"
    
    # Check if already downloaded
    if zip_path.exists():
        logger.info(f"Dataset already downloaded: {zip_path}")
    else:
        logger.info(f"Downloading MovieLens {dataset_size} dataset...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Download complete: {zip_path}")
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            return False
    
    # Extract
    extract_dir = data_dir / f"ml-{dataset_size}"
    if not extract_dir.exists():
        logger.info("Extracting dataset...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            logger.info(f"Extraction complete: {extract_dir}")
        except Exception as e:
            logger.error(f"Error extracting dataset: {str(e)}")
            return False
    
    return True


def load_movielens_1m():
    """Load MovieLens 1M dataset"""
    data_dir = Path("data/ml-1m")
    
    if not data_dir.exists():
        logger.error(f"Dataset directory not found: {data_dir}")
        logger.info("Run download_movielens_dataset() first")
        return None, None, None
    
    try:
        # Load movies (MovieID::Title::Genres)
        logger.info("Loading movies...")
        movies = pd.read_csv(
            data_dir / "movies.dat",
            sep='::',
            engine='python',
            encoding='latin-1',
            names=['MovieID', 'Title', 'Genres'],
            dtype={'MovieID': int, 'Title': str, 'Genres': str}
        )
        
        # Load ratings (UserID::MovieID::Rating::Timestamp)
        logger.info("Loading ratings...")
        ratings = pd.read_csv(
            data_dir / "ratings.dat",
            sep='::',
            engine='python',
            names=['UserID', 'MovieID', 'Rating', 'Timestamp'],
            dtype={'UserID': int, 'MovieID': int, 'Rating': float, 'Timestamp': int}
        )
        
        # Load users (UserID::Gender::Age::Occupation::Zip-code)
        logger.info("Loading users...")
        users = pd.read_csv(
            data_dir / "users.dat",
            sep='::',
            engine='python',
            names=['UserID', 'Gender', 'Age', 'Occupation', 'Zipcode'],
            dtype={'UserID': int, 'Gender': str, 'Age': int, 'Occupation': int, 'Zipcode': str}
        )
        
        logger.info(f"Loaded {len(movies)} movies, {len(ratings)} ratings, {len(users)} users")
        return movies, ratings, users
        
    except Exception as e:
        logger.error(f"Error loading MovieLens data: {str(e)}")
        return None, None, None


def load_movielens_25m():
    """Load MovieLens 25M dataset (MEMORY-OPTIMIZED)"""
    data_dir = Path("data/ml-25m")
    
    if not data_dir.exists():
        logger.error(f"Dataset directory not found: {data_dir}")
        return None, None
    
    try:
        # Load movies (movieId,title,genres)
        logger.info("Loading movies...")
        movies = pd.read_csv(data_dir / "movies.csv")
        
        # Load ratings with optimized dtypes (userId,movieId,rating,timestamp)
        logger.info("Loading ratings (memory-optimized)...")
        logger.info("⚠️  This is a large file, using optimized loading...")
        ratings = pd.read_csv(
            data_dir / "ratings.csv",
            dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32', 'timestamp': 'int64'},
            usecols=['userId', 'movieId', 'rating', 'timestamp']  # Only load needed columns
        )
        
        logger.info(f"Loaded {len(movies)} movies, {len(ratings)} ratings")
        logger.info(f"Memory usage: {ratings.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        return movies, ratings
        
    except Exception as e:
        logger.error(f"Error loading MovieLens 25M data: {str(e)}")
        return None, None


def import_to_database(movies_df, ratings_df, users_df=None, limit_movies=1000, limit_ratings=10000):
    """
    Import MovieLens data to database (MEMORY-OPTIMIZED)
    
    Args:
        movies_df: Movies DataFrame
        ratings_df: Ratings DataFrame
        users_df: Users DataFrame (optional)
        limit_movies: Maximum number of movies to import
        limit_ratings: Maximum number of ratings to import
    """
    import gc
    try:
        init_db()
        
        with get_db_context() as db:
            # Import Movies
            logger.info(f"Importing movies (limit: {limit_movies})...")
            movies_added = 0
            
            for idx, row in movies_df.head(limit_movies).iterrows():
                try:
                    # Check if movie exists
                    movie_id = int(row.get('MovieID', row.get('movieId')))
                    existing = db.query(Movie).filter(Movie.id == movie_id).first()
                    
                    if existing:
                        continue
                    
                    # Parse title and year
                    title = row.get('Title', row.get('title', ''))
                    year = None
                    if '(' in title and ')' in title:
                        year_str = title[title.rfind('(')+1:title.rfind(')')]
                        if year_str.isdigit():
                            year = year_str
                            title = title[:title.rfind('(')].strip()
                    
                    # Parse genres
                    genres_str = row.get('Genres', row.get('genres', ''))
                    genres_list = genres_str.split('|')
                    genres_json = json.dumps([{"name": g} for g in genres_list if g != '(no genres listed)'])
                    
                    # Create movie
                    movie = Movie(
                        id=movie_id,
                        title=title,
                        overview=f"A {genres_str.replace('|', ', ')} movie",
                        release_date=f"{year}-01-01" if year else None,
                        genres=genres_json,
                        vote_average=0.0,
                        vote_count=0,
                        popularity=0.0
                    )
                    
                    db.add(movie)
                    movies_added += 1
                    
                    if movies_added % 100 == 0:
                        db.commit()
                        logger.info(f"Imported {movies_added} movies...")
                        
                except Exception as e:
                    logger.error(f"Error importing movie {idx}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Movies import complete: {movies_added} added")
            
            # Clean up
            gc.collect()
            
            # Import Users
            if users_df is not None:
                logger.info("Importing users...")
                users_added = 0
                
                for idx, row in users_df.iterrows():
                    try:
                        user_id = f"ml_user_{row['UserID']}"
                        existing = db.query(User).filter(User.id == user_id).first()
                        
                        if existing:
                            continue
                        
                        # Create user
                        user = User(
                            id=user_id,
                            username=f"user_{row['UserID']}",
                            email=f"user{row['UserID']}@movielens.org",
                            password_hash=hashlib.sha256(f"password{row['UserID']}".encode()).hexdigest(),
                            favorite_genres=json.dumps([])
                        )
                        
                        db.add(user)
                        users_added += 1
                        
                        if users_added % 100 == 0:
                            db.commit()
                            logger.info(f"Imported {users_added} users...")
                            
                    except Exception as e:
                        logger.error(f"Error importing user {idx}: {str(e)}")
                        continue
                
                db.commit()
                logger.info(f"Users import complete: {users_added} added")
            
            # Import Ratings
            logger.info(f"Importing ratings (limit: {limit_ratings})...")
            ratings_added = 0
            
            # Sample ratings if too many
            if len(ratings_df) > limit_ratings:
                ratings_sample = ratings_df.sample(n=limit_ratings, random_state=42)
            else:
                ratings_sample = ratings_df
            
            for idx, row in ratings_sample.iterrows():
                try:
                    user_id = f"ml_user_{row.get('UserID', row.get('userId'))}"
                    movie_id = int(row.get('MovieID', row.get('movieId')))
                    rating_value = float(row.get('Rating', row.get('rating')))
                    timestamp = int(row.get('Timestamp', row.get('timestamp', 0)))
                    
                    # Check if user and movie exist
                    user_exists = db.query(User).filter(User.id == user_id).first()
                    movie_exists = db.query(Movie).filter(Movie.id == movie_id).first()
                    
                    if not user_exists or not movie_exists:
                        continue
                    
                    # Check if rating exists
                    existing_rating = db.query(Rating).filter(
                        Rating.user_id == user_id,
                        Rating.movie_id == movie_id
                    ).first()
                    
                    if existing_rating:
                        continue
                    
                    # Create rating
                    rating = Rating(
                        id=f"ml_rating_{user_id}_{movie_id}",
                        user_id=user_id,
                        movie_id=movie_id,
                        rating=rating_value,
                        timestamp=datetime.fromtimestamp(timestamp) if timestamp > 0 else datetime.utcnow()
                    )
                    
                    db.add(rating)
                    ratings_added += 1
                    
                    if ratings_added % 500 == 0:
                        db.commit()
                        logger.info(f"Imported {ratings_added} ratings...")
                        
                except Exception as e:
                    logger.error(f"Error importing rating {idx}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Ratings import complete: {ratings_added} added")
            
            # Clean up
            gc.collect()
            return True
            
    except Exception as e:
        logger.error(f"Error importing to database: {str(e)}")
        return False


def train_models_on_movielens():
    """Train ML models on MovieLens data from database"""
    try:
        from ml.collaborative_filtering import CollaborativeFilteringModel
        
        logger.info("Training models on MovieLens data...")
        
        with get_db_context() as db:
            # Get all ratings
            ratings = db.query(Rating).all()
            movies = db.query(Movie).all()
            
            if not ratings or not movies:
                logger.error("No data found in database")
                return False
            
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
            
            logger.info(f"Training on {len(ratings_data)} ratings and {len(movies_data)} movies")
            
            # Train collaborative filtering model
            model = CollaborativeFilteringModel()
            
            # Prepare data
            if not model.prepare_data(ratings_data, movies_data):
                logger.error("Failed to prepare data")
                return False
            
            # Compute similarities
            if not model.compute_user_similarity():
                logger.error("Failed to compute user similarity")
                return False
            
            # Train SVD model
            if not model.train_svd_model(n_components=50):
                logger.error("Failed to train SVD model")
                return False
            
            # Train KNN model
            if not model.train_knn_model(n_neighbors=20):
                logger.error("Failed to train KNN model")
                return False
            
            # Save model
            model_dir = Path("models")
            model_dir.mkdir(exist_ok=True)
            model_path = model_dir / "collaborative_filtering_movielens.pkl"
            
            if model.save_model(str(model_path)):
                logger.info(f"Model saved to {model_path}")
            else:
                logger.error("Failed to save model")
                return False
            
            logger.info("✅ Model training complete!")
            logger.info(f"RMSE: {model.rmse}, MAE: {model.mae}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load MovieLens dataset and train models")
    parser.add_argument("--download", action="store_true", help="Download dataset")
    parser.add_argument("--dataset", choices=["1m", "25m"], default="1m", help="Dataset size")
    parser.add_argument("--import", dest="import_data", action="store_true", help="Import to database")
    parser.add_argument("--train", action="store_true", help="Train models")
    parser.add_argument("--limit-movies", type=int, default=1000, help="Max movies to import")
    parser.add_argument("--limit-ratings", type=int, default=10000, help="Max ratings to import")
    parser.add_argument("--all", action="store_true", help="Download, import, and train")
    
    args = parser.parse_args()
    
    if args.all:
        args.download = True
        args.import_data = True
        args.train = True
    
    if args.download:
        logger.info(f"Downloading MovieLens {args.dataset} dataset...")
        if not download_movielens_dataset(args.dataset):
            logger.error("Download failed")
            exit(1)
    
    if args.import_data:
        logger.info("Loading dataset...")
        if args.dataset == "1m":
            movies_df, ratings_df, users_df = load_movielens_1m()
        else:
            movies_df, ratings_df = load_movielens_25m()
            users_df = None
        
        if movies_df is None:
            logger.error("Failed to load dataset")
            exit(1)
        
        logger.info("Importing to database...")
        if not import_to_database(movies_df, ratings_df, users_df, args.limit_movies, args.limit_ratings):
            logger.error("Import failed")
            exit(1)
    
    if args.train:
        logger.info("Training models...")
        if not train_models_on_movielens():
            logger.error("Training failed")
            exit(1)
    
    logger.info("✅ All operations completed successfully!")
