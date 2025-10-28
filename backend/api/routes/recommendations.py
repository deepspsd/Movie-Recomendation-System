from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Movie, Rating
from schemas import RecommendationResponse, MoodRecommendationRequest, WatchPartyRequest, WatchPartyResponse, MovieResponse
from utils.auth_middleware import get_current_user
from ml.collaborative_filtering import CollaborativeFilteringModel
from ml.content_based_filtering import ContentBasedFilteringModel
from ml.hybrid_recommender import AdaptiveHybridRecommender
from ml.evaluation_metrics import RecommendationEvaluator
from ml.model_persistence import ModelPersistence
from services.omdb_service import omdb_service
from services.tmdb_service import tmdb_service
import random
import json
import logging
import os
from typing import List, Dict, Set
from datetime import datetime

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
logger = logging.getLogger(__name__)

# Global recommendation model instances
recommendation_model = None
content_model = None
hybrid_model = None
evaluator = None
models_loaded = False

# Track recommended movies per user to prevent duplicates in session
user_recommended_movies: Dict[str, Set[int]] = {}


def get_popular_movies(db: Session, limit: int = 20) -> List[Movie]:
    """Get popular movies based on vote count and average rating"""
    movies = db.query(Movie).filter(
        Movie.vote_count >= 100,
        Movie.vote_average >= 6.0
    ).order_by(Movie.popularity.desc()).limit(limit * 2).all()
    
    # Enrich movies without posters
    movies_to_enrich = [m for m in movies if not m.poster_path or m.poster_path == 'N/A'][:limit]
    if movies_to_enrich:
        logger.info(f"Enriching {len(movies_to_enrich)} popular movies with OMDB data")
        enriched = enrich_movies_with_external_data(movies_to_enrich, db)
        enriched_dict = {m.id: m for m in enriched}
        result = []
        for movie in movies:
            if movie.id in enriched_dict:
                result.append(enriched_dict[movie.id])
            elif movie.poster_path and movie.poster_path != 'N/A':
                result.append(movie)
            if len(result) >= limit:
                break
        return result[:limit]
    
    return movies[:limit]


def get_user_ratings(db: Session, user_id: str) -> List[Rating]:
    """Get all ratings for a user"""
    return db.query(Rating).filter(Rating.user_id == user_id).all()


def get_similar_users(db: Session, user_id: str) -> List[str]:
    """Find users with similar rating patterns (simplified)"""
    # For a mini project, we'll just return some random users
    all_users = db.query(User.id).filter(User.id != user_id).limit(10).all()
    return [user[0] for user in all_users[:3]]  # Return up to 3 similar users


def get_collaborative_recommendations(db: Session, user_id: str, limit: int = 10) -> List[Movie]:
    """Get collaborative filtering recommendations"""
    # Simplified collaborative filtering for mini project
    similar_users = get_similar_users(db, user_id)
    
    if not similar_users:
        return get_popular_movies(db, limit)
    
    # Get highly rated movies from similar users
    recommended_movies = db.query(Movie).join(Rating).filter(
        Rating.user_id.in_(similar_users),
        Rating.rating >= 4.0
    ).distinct().limit(limit).all()
    
    # If we don't have enough recommendations, fill with popular movies
    if len(recommended_movies) < limit:
        additional_movies = get_popular_movies(db, limit - len(recommended_movies))
        recommended_movies.extend(additional_movies)
    
    return recommended_movies[:limit]


def get_content_based_recommendations(db: Session, movie_id: int, limit: int = 10) -> List[Movie]:
    """Get content-based recommendations (simplified)"""
    # For mini project, we'll just get movies from the same genre
    target_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not target_movie:
        return get_popular_movies(db, limit)
    
    # Get movies with similar genres (simplified)
    similar_movies = db.query(Movie).filter(
        Movie.id != movie_id,
        Movie.vote_average >= 6.0
    ).order_by(Movie.popularity.desc()).limit(limit).all()
    
    return similar_movies


def get_mood_recommendations(db: Session, mood: str, limit: int = 20) -> List[Movie]:
    """Get mood-based recommendations with intelligent genre matching using OMDB"""
    
    # Define mood-specific search terms and IMDb IDs for different moods
    mood_config = {
        "happy": {
            "genres": ["comedy", "family", "animation", "music"],
            "search_terms": ["comedy", "funny", "happy", "family", "animation"],
            "imdb_ids": [
                "tt0109830",  # Forrest Gump
                "tt0110912",  # Pulp Fiction
                "tt0120737",  # LOTR Fellowship
                "tt0317248",  # City of God
                "tt0245429",  # Spirited Away
                "tt0118799",  # Life Is Beautiful
                "tt0088763",  # Back to the Future
                "tt0266543",  # Finding Nemo
                "tt0435761",  # Toy Story 3
                "tt1049413",  # Up
                "tt0892769",  # How to Train Your Dragon
                "tt2380307",  # Coco
                "tt0910970",  # WALL-E
                "tt0120689",  # The Green Mile
                "tt0095327",  # Grave of the Fireflies
            ]
        },
        "sad": {
            "genres": ["drama", "romance"],
            "search_terms": ["drama", "emotional", "sad", "romance"],
            "imdb_ids": [
                "tt0108052",  # Schindler's List
                "tt0118799",  # Life Is Beautiful
                "tt0120689",  # The Green Mile
                "tt0253474",  # The Pianist
                "tt0095327",  # Grave of the Fireflies
                "tt0405094",  # The Lives of Others
                "tt0364569",  # Oldboy
                "tt0050083",  # 12 Angry Men
                "tt0071562",  # The Godfather Part II
                "tt0043014",  # Sunset Boulevard
                "tt1675434",  # The Intouchables
                "tt0338013",  # Eternal Sunshine
                "tt0361748",  # Inglourious Basterds
            ]
        },
        "adventurous": {
            "genres": ["action", "adventure", "thriller", "fantasy"],
            "search_terms": ["action", "adventure", "thriller", "epic"],
            "imdb_ids": [
                "tt0468569",  # The Dark Knight
                "tt0167260",  # LOTR Return of the King
                "tt0167261",  # LOTR Two Towers
                "tt0120737",  # LOTR Fellowship
                "tt0137523",  # Fight Club
                "tt1375666",  # Inception
                "tt0133093",  # The Matrix
                "tt0076759",  # Star Wars IV
                "tt0080684",  # Star Wars V
                "tt0816692",  # Interstellar
                "tt0103064",  # Terminator 2
                "tt0082971",  # Raiders of the Lost Ark
                "tt0120815",  # Saving Private Ryan
                "tt1345836",  # The Dark Knight Rises
                "tt0407887",  # The Departed
                "tt0482571",  # The Prestige
            ]
        },
        "romantic": {
            "genres": ["romance", "comedy"],
            "search_terms": ["romance", "love", "romantic"],
            "imdb_ids": [
                "tt0034583",  # Casablanca
                "tt0038650",  # It's a Wonderful Life
                "tt0338013",  # Eternal Sunshine
                "tt0110413",  # Léon: The Professional
                "tt0119217",  # Good Will Hunting
                "tt0112573",  # Braveheart
                "tt0361748",  # Inglourious Basterds
                "tt1675434",  # The Intouchables
                "tt0050083",  # 12 Angry Men
                "tt0118799",  # Life Is Beautiful
            ]
        },
        "scared": {
            "genres": ["horror", "thriller", "mystery"],
            "search_terms": ["horror", "thriller", "scary", "suspense"],
            "imdb_ids": [
                "tt0102926",  # The Silence of the Lambs
                "tt0114369",  # Se7en
                "tt0078748",  # Alien
                "tt0078788",  # Apocalypse Now
                "tt0054215",  # Psycho
                "tt0047396",  # Rear Window
                "tt0114814",  # The Usual Suspects
                "tt0209144",  # Memento
                "tt0120586",  # American History X
                "tt0364569",  # Oldboy
                "tt0405094",  # The Lives of Others
                "tt0110413",  # Léon: The Professional
            ]
        },
        "thoughtful": {
            "genres": ["drama", "documentary", "sci-fi", "history"],
            "search_terms": ["drama", "philosophical", "thought-provoking"],
            "imdb_ids": [
                "tt0111161",  # The Shawshank Redemption
                "tt0068646",  # The Godfather
                "tt0071562",  # The Godfather Part II
                "tt0050083",  # 12 Angry Men
                "tt0108052",  # Schindler's List
                "tt0073486",  # One Flew Over the Cuckoo's Nest
                "tt0099685",  # Goodfellas
                "tt0060196",  # The Good, the Bad and the Ugly
                "tt0027977",  # Modern Times
                "tt0021749",  # City Lights
                "tt0064116",  # Once Upon a Time in the West
                "tt0253474",  # The Pianist
                "tt0816692",  # Interstellar
                "tt1375666",  # Inception
                "tt0133093",  # The Matrix
            ]
        }
    }
    
    config = mood_config.get(mood.lower(), mood_config["thoughtful"])
    genres = config["genres"]
    imdb_ids = config["imdb_ids"]
    
    try:
        logger.info(f"Getting mood recommendations for: {mood}")
        
        # Fetch mood-specific movies from OMDB using IMDb IDs
        mood_movies = []
        seen_ids = set()
        
        for imdb_id in imdb_ids:
            if len(mood_movies) >= limit:
                break
                
            try:
                omdb_movie = omdb_service.get_movie_by_id(imdb_id)
                if omdb_movie and omdb_movie['id'] not in seen_ids:
                    seen_ids.add(omdb_movie['id'])
                    
                    # Check if movie exists in DB, otherwise create temporary object
                    movie = db.query(Movie).filter(Movie.id == omdb_movie['id']).first()
                    if not movie:
                        movie = Movie(
                            id=omdb_movie['id'],
                            title=omdb_movie['title'],
                            overview=omdb_movie.get('overview', ''),
                            poster_path=omdb_movie.get('poster_path'),
                            backdrop_path=omdb_movie.get('backdrop_path'),
                            release_date=omdb_movie.get('release_date'),
                            vote_average=omdb_movie.get('vote_average', 0),
                            vote_count=omdb_movie.get('vote_count', 0),
                            popularity=omdb_movie.get('popularity', 0),
                            genres=json.dumps(omdb_movie.get('genres', [])),
                            runtime=omdb_movie.get('runtime', 0)
                        )
                    else:
                        # Update with OMDB poster if missing
                        if not movie.poster_path:
                            movie.poster_path = omdb_movie.get('poster_path')
                        if not movie.backdrop_path:
                            movie.backdrop_path = omdb_movie.get('backdrop_path')
                    mood_movies.append(movie)
            except Exception as e:
                logger.debug(f"Failed to fetch movie {imdb_id}: {str(e)}")
                continue
        
        if mood_movies:
            logger.info(f"Found {len(mood_movies)} OMDB movies for mood: {mood}")
            return mood_movies[:limit]
        
        # Fallback: Query database movies
        logger.info("Falling back to database movies for mood recommendations")
        movies = db.query(Movie).filter(
            Movie.vote_average >= 7.0,
            Movie.vote_count >= 50
        ).all()
        
        # Filter by genre
        db_mood_movies = []
        for movie in movies:
            if movie.genres:
                try:
                    movie_genres = json.loads(movie.genres) if isinstance(movie.genres, str) else movie.genres
                    movie_genre_names = [g['name'].lower() if isinstance(g, dict) else str(g).lower() for g in movie_genres]
                    
                    if any(genre.lower() in movie_genre_names for genre in genres):
                        db_mood_movies.append(movie)
                except:
                    pass
        
        # Sort by rating and popularity
        db_mood_movies.sort(key=lambda m: (m.vote_average * 0.7 + (m.popularity / 100) * 0.3), reverse=True)
        
        # Enrich with OMDB posters
        movies_to_enrich = [m for m in db_mood_movies[:limit] if not m.poster_path]
        if movies_to_enrich:
            enriched = enrich_movies_with_external_data(movies_to_enrich, db)
            enriched_dict = {m.id: m for m in enriched}
            result = []
            for movie in db_mood_movies[:limit]:
                if movie.id in enriched_dict:
                    result.append(enriched_dict[movie.id])
                elif movie.poster_path:
                    result.append(movie)
            return result if result else get_popular_movies(db, limit)
        
        return db_mood_movies[:limit] if db_mood_movies else get_popular_movies(db, limit)
    except Exception as e:
        logger.error(f"Error in mood recommendations: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return get_popular_movies(db, limit)


def get_intelligent_fallback_recommendations(db: Session, user_id: str, limit: int = 10, mood: str = None) -> List[Movie]:
    """
    WORLD-CLASS INTELLIGENT FALLBACK SYSTEM
    Returns high-quality, diverse recommendations when ML model fails or for new users
    Focuses on hidden gems and underrated movies
    Uses OMDB best movies as fallback to ensure posters are available
    """
    try:
        # First, try to get OMDB best movies which have posters
        logger.info("Using OMDB best movies as fallback recommendations")
        omdb_movies = omdb_service.get_best_movies(limit=limit)
        if omdb_movies and len(omdb_movies) >= limit:
            # Convert OMDB data to Movie objects
            fallback_movies = []
            for omdb_movie in omdb_movies[:limit]:
                # Check if movie exists in DB
                movie = db.query(Movie).filter(Movie.id == omdb_movie['id']).first()
                if not movie:
                    # Create temporary Movie object
                    movie = Movie(
                        id=omdb_movie['id'],
                        title=omdb_movie['title'],
                        overview=omdb_movie.get('overview', ''),
                        poster_path=omdb_movie.get('poster_path'),
                        backdrop_path=omdb_movie.get('backdrop_path'),
                        release_date=omdb_movie.get('release_date'),
                        vote_average=omdb_movie.get('vote_average', 0),
                        vote_count=omdb_movie.get('vote_count', 0),
                        popularity=omdb_movie.get('popularity', 0),
                        genres=json.dumps(omdb_movie.get('genres', [])),
                        runtime=omdb_movie.get('runtime', 0)
                    )
                else:
                    # Update existing movie with OMDB data if missing
                    if not movie.poster_path:
                        movie.poster_path = omdb_movie.get('poster_path')
                    if not movie.backdrop_path:
                        movie.backdrop_path = omdb_movie.get('backdrop_path')
                fallback_movies.append(movie)
            
            if len(fallback_movies) >= limit:
                logger.info(f"Returning {len(fallback_movies)} OMDB best movies as fallback")
                return fallback_movies[:limit]
        
        # Original fallback logic if OMDB fails
        # Get user preferences if available
        user = db.query(User).filter(User.id == user_id).first()
        favorite_genres = []
        if user and user.favorite_genres:
            try:
                favorite_genres = json.loads(user.favorite_genres)
            except:
                pass
        
        # Strategy 1: Hidden Gems (High quality, lower popularity)
        hidden_gems = db.query(Movie).filter(
            Movie.vote_average >= 7.5,  # High quality
            Movie.vote_count >= 100,     # Enough votes to be reliable
            Movie.vote_count <= 5000,    # Not too popular (hidden gem)
            Movie.popularity < 50         # Lower popularity score
        ).order_by(
            Movie.vote_average.desc(),
            Movie.vote_count.desc()
        ).limit(limit * 2).all()
        
        # Strategy 2: Critically Acclaimed (Very high ratings)
        acclaimed = db.query(Movie).filter(
            Movie.vote_average >= 8.0,
            Movie.vote_count >= 500
        ).order_by(
            Movie.vote_average.desc()
        ).limit(limit).all()
        
        # Strategy 3: Genre-based if user has preferences
        genre_based = []
        if favorite_genres:
            all_movies = db.query(Movie).filter(
                Movie.vote_average >= 7.0,
                Movie.vote_count >= 100
            ).all()
            
            for movie in all_movies:
                if movie.genres:
                    try:
                        movie_genres = json.loads(movie.genres) if isinstance(movie.genres, str) else movie.genres
                        movie_genre_names = [g['name'] if isinstance(g, dict) else str(g) for g in movie_genres]
                        
                        if any(fav in movie_genre_names for fav in favorite_genres):
                            genre_based.append(movie)
                    except:
                        pass
            
            genre_based.sort(key=lambda m: m.vote_average, reverse=True)
            genre_based = genre_based[:limit]
        
        # Strategy 4: Mood-based if mood provided
        mood_based = []
        if mood:
            mood_based = get_mood_recommendations(db, mood, limit)
        
        # Combine strategies with diversity
        combined = []
        seen_ids = set()
        
        # Add from each strategy to ensure diversity
        sources = [hidden_gems, acclaimed, genre_based, mood_based]
        max_per_source = max(2, limit // len([s for s in sources if s]))
        
        for source in sources:
            count = 0
            for movie in source:
                if movie.id not in seen_ids and count < max_per_source:
                    combined.append(movie)
                    seen_ids.add(movie.id)
                    count += 1
                    if len(combined) >= limit:
                        break
            if len(combined) >= limit:
                break
        
        # Fill remaining with hidden gems
        for movie in hidden_gems:
            if movie.id not in seen_ids and len(combined) < limit:
                combined.append(movie)
                seen_ids.add(movie.id)
        
        logger.info(f"Intelligent fallback returned {len(combined)} diverse recommendations")
        return combined[:limit]
        
    except Exception as e:
        logger.error(f"Error in intelligent fallback: {str(e)}")
        return get_popular_movies(db, limit)


def get_cold_start_recommendations(db: Session, user_id: str, limit: int = 10, mood: str = None) -> List[Movie]:
    """
    WORLD-CLASS COLD START STRATEGY FOR NEW USERS
    Provides diverse, high-quality recommendations to help users discover their taste
    Uses OMDB popular and best movies to ensure posters are available
    """
    try:
        logger.info(f"Cold start recommendations for new user {user_id}")
        
        # Use OMDB popular movies for new users (they have posters)
        omdb_popular = omdb_service.get_popular_movies(limit=limit)
        if omdb_popular and len(omdb_popular) >= limit:
            cold_start_movies = []
            for omdb_movie in omdb_popular[:limit]:
                movie = db.query(Movie).filter(Movie.id == omdb_movie['id']).first()
                if not movie:
                    movie = Movie(
                        id=omdb_movie['id'],
                        title=omdb_movie['title'],
                        overview=omdb_movie.get('overview', ''),
                        poster_path=omdb_movie.get('poster_path'),
                        backdrop_path=omdb_movie.get('backdrop_path'),
                        release_date=omdb_movie.get('release_date'),
                        vote_average=omdb_movie.get('vote_average', 0),
                        vote_count=omdb_movie.get('vote_count', 0),
                        popularity=omdb_movie.get('popularity', 0),
                        genres=json.dumps(omdb_movie.get('genres', [])),
                        runtime=omdb_movie.get('runtime', 0)
                    )
                else:
                    if not movie.poster_path:
                        movie.poster_path = omdb_movie.get('poster_path')
                    if not movie.backdrop_path:
                        movie.backdrop_path = omdb_movie.get('backdrop_path')
                cold_start_movies.append(movie)
            
            if len(cold_start_movies) >= limit:
                logger.info(f"Returning {len(cold_start_movies)} OMDB popular movies for cold start")
                return cold_start_movies[:limit]
        
        # Original cold start logic if OMDB fails
        
        # Strategy: Diverse mix of genres and styles
        # 1. Universally acclaimed movies (everyone loves these)
        universal = db.query(Movie).filter(
            Movie.vote_average >= 8.0,
            Movie.vote_count >= 1000
        ).order_by(Movie.vote_average.desc()).limit(3).all()
        
        # 2. Popular recent movies (current trends)
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
        recent = db.query(Movie).filter(
            Movie.release_date >= recent_date,
            Movie.vote_average >= 7.0,
            Movie.vote_count >= 500
        ).order_by(Movie.popularity.desc()).limit(3).all()
        
        # 3. Hidden gems (help users discover)
        gems = db.query(Movie).filter(
            Movie.vote_average >= 7.5,
            Movie.vote_count.between(200, 2000),
            Movie.popularity < 30
        ).order_by(Movie.vote_average.desc()).limit(3).all()
        
        # 4. Diverse genres
        diverse = []
        target_genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Thriller', 'Romance']
        for genre in target_genres:
            genre_movies = db.query(Movie).filter(
                Movie.vote_average >= 7.0,
                Movie.vote_count >= 300
            ).all()
            
            for movie in genre_movies:
                if movie.genres:
                    try:
                        movie_genres = json.loads(movie.genres) if isinstance(movie.genres, str) else movie.genres
                        genre_names = [g['name'] if isinstance(g, dict) else str(g) for g in movie_genres]
                        if genre in genre_names:
                            diverse.append(movie)
                            break
                    except:
                        pass
        
        # Combine with diversity
        combined = []
        seen_ids = set()
        
        for source in [universal, recent, gems, diverse]:
            for movie in source:
                if movie.id not in seen_ids:
                    combined.append(movie)
                    seen_ids.add(movie.id)
                    if len(combined) >= limit:
                        break
            if len(combined) >= limit:
                break
        
        logger.info(f"Cold start returned {len(combined)} diverse recommendations")
        return combined[:limit]
        
    except Exception as e:
        logger.error(f"Error in cold start: {str(e)}")
        return get_intelligent_fallback_recommendations(db, user_id, limit, mood)


def get_watch_party_recommendations(db: Session, user_ids: List[str], limit: int = 10) -> List[Movie]:
    """Get watch party recommendations based on group preferences"""
    try:
        # Get all ratings from group members
        group_ratings = db.query(Rating).filter(Rating.user_id.in_(user_ids)).all()
        
        if not group_ratings:
            return get_popular_movies(db, limit)
        
        # Calculate average ratings for movies rated by group
        movie_ratings = {}
        for rating in group_ratings:
            if rating.movie_id not in movie_ratings:
                movie_ratings[rating.movie_id] = []
            movie_ratings[rating.movie_id].append(rating.rating)
        
        # Calculate average ratings and find highly rated movies
        avg_ratings = {}
        for movie_id, ratings in movie_ratings.items():
            avg_ratings[movie_id] = sum(ratings) / len(ratings)
        
        # Sort by average rating and get top movies
        sorted_movies = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
        top_movie_ids = [movie_id for movie_id, _ in sorted_movies[:limit]]
        
        # Get movie objects
        movies = db.query(Movie).filter(Movie.id.in_(top_movie_ids)).all()
        return movies[:limit]
        
    except Exception as e:
        logger.error(f"Error getting watch party recommendations: {str(e)}")
        return get_popular_movies(db, limit)


def initialize_recommendation_model(db: Session, force_retrain: bool = False):
    """Initialize all recommendation models with current data or load from disk"""
    global recommendation_model, content_model, hybrid_model, evaluator, models_loaded
    
    try:
        # Try to load the trained model from saved_models directory first
        if not force_retrain and not models_loaded:
            logger.info("Attempting to load trained model from saved_models directory...")
            
            # Check for the uploaded trained model
            trained_model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'collaborative_filtering_trained.pkl')
            
            if os.path.exists(trained_model_path):
                try:
                    recommendation_model = CollaborativeFilteringModel()
                    success = recommendation_model.load_model(trained_model_path)
                    
                    if success:
                        logger.info(f"✅ Loaded trained model from {trained_model_path}")
                        
                        # Also try to load other models from ModelPersistence
                        loaded_content = ModelPersistence.load_model('content_model')
                        loaded_hybrid = ModelPersistence.load_model('hybrid_model')
                        
                        if loaded_content:
                            content_model = loaded_content
                            logger.info("✅ Content model loaded from disk")
                        
                        if loaded_hybrid:
                            hybrid_model = loaded_hybrid
                            logger.info("✅ Hybrid model loaded from disk")
                        
                        evaluator = RecommendationEvaluator()
                        models_loaded = True
                        logger.info("🎉 All models loaded successfully!")
                        return
                except Exception as e:
                    logger.warning(f"Failed to load trained model: {str(e)}")
            
            # Fallback to ModelPersistence
            logger.info("Attempting to load models from ModelPersistence...")
            
            # Check if models should be retrained (older than 24 hours)
            should_retrain = (
                ModelPersistence.should_retrain('collaborative_model', max_age_hours=24) or
                ModelPersistence.should_retrain('content_model', max_age_hours=24) or
                ModelPersistence.should_retrain('hybrid_model', max_age_hours=24)
            )
            
            if not should_retrain:
                # Try loading from disk
                loaded_collab = ModelPersistence.load_model('collaborative_model')
                loaded_content = ModelPersistence.load_model('content_model')
                loaded_hybrid = ModelPersistence.load_model('hybrid_model')
                
                if loaded_collab and loaded_content and loaded_hybrid:
                    recommendation_model = loaded_collab
                    content_model = loaded_content
                    hybrid_model = loaded_hybrid
                    evaluator = RecommendationEvaluator()
                    models_loaded = True
                    logger.info("✅ Models loaded successfully from disk!")
                    return
                else:
                    logger.info("Models not found on disk, training new models...")
            else:
                logger.info("Models are outdated, retraining...")
        
        # Train new models if not loaded
        if recommendation_model is None or force_retrain:
            logger.info("Training new recommendation models...")
            
            # Initialize collaborative filtering model
            recommendation_model = CollaborativeFilteringModel()
            
            # Get all ratings and movies
            ratings = db.query(Rating).all()
            movies = db.query(Movie).all()
            
            logger.info(f"Found {len(ratings)} ratings and {len(movies)} movies")
            
            # Convert to format expected by models
            ratings_data = []
            for rating in ratings:
                ratings_data.append({
                    'user_id': rating.user_id,
                    'movie_id': rating.movie_id,
                    'rating': rating.rating
                })
            
            movies_data = []
            for movie in movies:
                movies_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'overview': movie.overview or '',
                    'genres': movie.genres or '[]',
                    'popularity': movie.popularity or 0,
                    'vote_average': movie.vote_average or 0,
                    'vote_count': movie.vote_count or 0,
                    'runtime': movie.runtime or 0,
                    'release_date': movie.release_date or '',
                    'budget': getattr(movie, 'budget', 0) or 0,
                    'revenue': getattr(movie, 'revenue', 0) or 0,
                    'director_score': getattr(movie, 'director_score', 0) or 0,
                    'actor_score': getattr(movie, 'actor_score', 0) or 0
                })
            
            # Prepare and train collaborative filtering model
            if ratings_data and movies_data:
                recommendation_model.prepare_data(ratings_data, movies_data)
                recommendation_model.compute_user_similarity()
                recommendation_model.train_svd_model(n_components=50)
                recommendation_model.train_knn_model(n_neighbors=20)
                recommendation_model.train_als_model(n_factors=50, n_iterations=10, lambda_reg=0.1, dropout_rate=0.1)
                logger.info("✅ Collaborative filtering model trained successfully")
                
                # Save collaborative model
                ModelPersistence.save_model(
                    recommendation_model, 
                    'collaborative_model',
                    metadata={
                        'num_ratings': len(ratings_data),
                        'num_movies': len(movies_data),
                        'algorithm': 'collaborative_filtering'
                    }
                )
            
            # Initialize content-based filtering model
            content_model = ContentBasedFilteringModel()
            if movies_data:
                content_model.prepare_data(movies_data)
                content_model.build_tfidf_features('overview')
                content_model.build_genre_features()
                content_model.build_metadata_features()
                content_model.compute_similarity_matrix(use_combined=True)
                logger.info("✅ Content-based filtering model trained successfully")
                
                # Save content model
                ModelPersistence.save_model(
                    content_model,
                    'content_model',
                    metadata={
                        'num_movies': len(movies_data),
                        'algorithm': 'content_based_filtering'
                    }
                )
            
            # Initialize hybrid recommender
            hybrid_model = AdaptiveHybridRecommender()
            hybrid_model.set_models(content_model, recommendation_model)
            logger.info("✅ Hybrid recommender initialized successfully")
            
            # Save hybrid model
            ModelPersistence.save_model(
                hybrid_model,
                'hybrid_model',
                metadata={
                    'algorithm': 'hybrid_adaptive'
                }
            )
            
            # Initialize evaluator
            evaluator = RecommendationEvaluator()
            logger.info("✅ Evaluation metrics initialized successfully")
            
            models_loaded = True
            logger.info("🎉 All models trained and saved successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error initializing recommendation models: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def enrich_movies_with_external_data(movies: List[Movie], db: Session) -> List[Movie]:
    """Enrich movie data with OMDB information including posters and details"""
    enriched_movies = []
    
    for movie in movies:
        try:
            # Check if movie already has poster data
            if movie.poster_path and (movie.poster_path.startswith('http') or movie.poster_path.startswith('/')):
                # Already has valid poster data
                enriched_movies.append(movie)
                continue
            
            # Try to fetch from OMDB by title
            try:
                omdb_results = omdb_service.search_movies(movie.title, page=1)
                if omdb_results and omdb_results.get('movies') and len(omdb_results['movies']) > 0:
                    omdb_movie = omdb_results['movies'][0]
                    
                    # Update movie with OMDB data
                    if omdb_movie.get('poster_path') and omdb_movie['poster_path'] != 'N/A':
                        movie.poster_path = omdb_movie['poster_path']
                    if omdb_movie.get('backdrop_path') and omdb_movie['backdrop_path'] != 'N/A':
                        movie.backdrop_path = omdb_movie['backdrop_path']
                    if not movie.overview and omdb_movie.get('overview'):
                        movie.overview = omdb_movie['overview']
                    if omdb_movie.get('director'):
                        movie.director = omdb_movie.get('director')
                    if omdb_movie.get('cast'):
                        movie.cast = json.dumps(omdb_movie['cast'])
                    
                    logger.debug(f"Enriched movie '{movie.title}' with OMDB data")
            except Exception as e:
                logger.debug(f"OMDB fetch failed for movie '{movie.title}': {str(e)}")
            
            enriched_movies.append(movie)
            
        except Exception as e:
            logger.warning(f"Error enriching movie {movie.id}: {str(e)}")
            enriched_movies.append(movie)
    
    return enriched_movies


def get_advanced_recommendations(db: Session, user_id: str, algorithm: str = "hybrid", limit: int = 10, exclude_watched: bool = True, mood: str = None) -> List[Movie]:
    """Get advanced recommendations using ML algorithms with duplicate prevention and external data enrichment"""
    global recommendation_model, content_model, hybrid_model, user_recommended_movies
    
    try:
        # Initialize models if not done
        if recommendation_model is None:
            initialize_recommendation_model(db)
        
        if recommendation_model is None:
            logger.warning("Model not loaded, falling back to intelligent popular movies")
            return get_intelligent_fallback_recommendations(db, user_id, limit, mood)
        
        # Check if user exists in model (has ratings)
        user_has_ratings = db.query(Rating).filter(Rating.user_id == user_id).first() is not None
        
        # Get user's already rated/watched movies to exclude
        excluded_movie_ids = set()
        if exclude_watched:
            user_ratings = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
            excluded_movie_ids = {r.movie_id for r in user_ratings}
        
        # Also exclude previously recommended movies in this session
        if user_id in user_recommended_movies:
            excluded_movie_ids.update(user_recommended_movies[user_id])
        
        # For new users without ratings, use intelligent cold-start strategy
        if not user_has_ratings:
            logger.info(f"New user {user_id} detected, using cold-start strategy")
            return get_cold_start_recommendations(db, user_id, limit, mood)
        
        # Request more recommendations to account for filtering
        request_limit = limit * 3
        
        # Get recommendations based on algorithm
        if algorithm == "hybrid" and hybrid_model:
            # Use advanced hybrid recommender with adaptive weighting
            recommendations = hybrid_model.get_hybrid_recommendations(user_id, request_limit, use_adaptive=True)
        elif algorithm == "als":
            # Use ALS collaborative filtering
            recommendations = recommendation_model.get_als_recommendations(user_id, request_limit)
        elif algorithm == "svd":
            recommendations = recommendation_model.get_svd_recommendations(user_id, request_limit)
        elif algorithm == "collaborative":
            recommendations = recommendation_model.get_user_recommendations(user_id, request_limit)
        elif algorithm == "content" and content_model:
            # Get user's highly rated movies for content-based
            user_ratings = db.query(Rating).filter(
                Rating.user_id == user_id,
                Rating.rating >= 4.0
            ).all()
            liked_movies = [r.movie_id for r in user_ratings]
            recommendations = content_model.get_recommendations_for_user(liked_movies, request_limit)
        else:
            # Default to collaborative filtering from trained model
            recommendations = recommendation_model.get_user_recommendations(user_id, request_limit)
        
        if not recommendations:
            logger.info("No recommendations from model, using intelligent fallback")
            return get_intelligent_fallback_recommendations(db, user_id, limit, mood)
        
        # Filter out excluded movies and get unique recommendations
        filtered_recommendations = []
        seen_ids = set()
        
        for movie_id, score in recommendations:
            if movie_id not in excluded_movie_ids and movie_id not in seen_ids:
                filtered_recommendations.append((movie_id, score))
                seen_ids.add(movie_id)
                
                if len(filtered_recommendations) >= limit:
                    break
        
        if not filtered_recommendations:
            logger.info("All recommendations were filtered out, using intelligent fallback")
            return get_intelligent_fallback_recommendations(db, user_id, limit, mood)
        
        # Get movie objects from database
        movie_ids = [movie_id for movie_id, _ in filtered_recommendations]
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        
        # Sort by recommendation score
        movie_dict = {movie.id: movie for movie in movies}
        sorted_movies = []
        for movie_id, score in filtered_recommendations:
            if movie_id in movie_dict:
                sorted_movies.append(movie_dict[movie_id])
        
        # Enrich with external data (OMDB) - but only for movies missing posters
        movies_to_enrich = [m for m in sorted_movies[:limit] if not m.poster_path or m.poster_path == 'N/A']
        if movies_to_enrich:
            logger.info(f"Enriching {len(movies_to_enrich)} movies with OMDB data")
            enriched_movies = enrich_movies_with_external_data(movies_to_enrich, db)
            # Merge back with movies that already have posters
            enriched_dict = {m.id: m for m in enriched_movies}
            final_movies = []
            for movie in sorted_movies[:limit]:
                if movie.id in enriched_dict:
                    final_movies.append(enriched_dict[movie.id])
                else:
                    final_movies.append(movie)
        else:
            final_movies = sorted_movies[:limit]
        
        # Track these recommendations for this user
        if user_id not in user_recommended_movies:
            user_recommended_movies[user_id] = set()
        user_recommended_movies[user_id].update([m.id for m in final_movies])
        
        logger.info(f"Returning {len(final_movies)} unique recommendations for user {user_id}")
        return final_movies
        
    except Exception as e:
        logger.error(f"Error getting advanced recommendations: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return get_intelligent_fallback_recommendations(db, user_id, limit, mood)


@router.get("/", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    algorithm: str = "hybrid",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized movie recommendations for the current user
    Supports algorithms: hybrid, collaborative, content, als, svd
    """
    try:
        # Get advanced recommendations using ML algorithms
        movies = get_advanced_recommendations(db, current_user.id, algorithm, limit)
        
        return RecommendationResponse(
            movies=movies,
            algorithm=algorithm,
            explanation=f"Personalized recommendations using {algorithm.upper()} algorithm"
        )
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {str(e)}")
        # Fallback to popular movies
        movies = get_popular_movies(db, limit)
        return RecommendationResponse(
            movies=movies,
            algorithm="popular",
            explanation="Popular movies (fallback)"
        )


@router.get("/mood", response_model=RecommendationResponse)
async def get_mood_recommendations_endpoint(
    mood: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get movie recommendations based on user's mood with ML personalization
    Uses OMDB API to ensure movies have posters and details
    """
    try:
        # Use mood-based recommendations with OMDB (more reliable for mood matching)
        movies = get_mood_recommendations(db, mood, limit)
        
        # If we got movies, return them
        if movies and len(movies) > 0:
            logger.info(f"Returning {len(movies)} mood recommendations for: {mood}")
            return RecommendationResponse(
                movies=movies,
                algorithm="mood_based_omdb",
                explanation=f"Movies matching your {mood} mood, curated from top-rated films"
            )
        
        # Fallback: Try personalized recommendations with mood context
        logger.info("Falling back to personalized recommendations with mood context")
        movies = get_advanced_recommendations(db, current_user.id, "hybrid", limit, mood=mood)
        
        return RecommendationResponse(
            movies=movies,
            algorithm="mood_based_ml",
            explanation=f"Personalized {mood} mood recommendations using AI"
        )
    except Exception as e:
        logger.error(f"Error getting mood recommendations: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Final fallback to popular movies
        movies = get_popular_movies(db, limit)
        return RecommendationResponse(
            movies=movies,
            algorithm="popular",
            explanation=f"Popular movies (fallback)"
        )


@router.get("/similar/{movie_id}", response_model=List[MovieResponse])
async def get_similar_movies(movie_id: int, db: Session = Depends(get_db)):
    """
    Get movies similar to the specified movie
    """
    similar_movies = get_content_based_recommendations(db, movie_id, 10)
    return similar_movies


@router.post("/group", response_model=WatchPartyResponse)
async def get_watch_party_recommendations_endpoint(
    request: WatchPartyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get movie recommendations for a group of users (watch party)
    """
    try:
        # Add current user to the group if not already included
        user_ids = list(request.user_ids)
        if current_user.id not in user_ids:
            user_ids.append(current_user.id)
        
        movies = get_watch_party_recommendations(db, user_ids, 10)
        
        # Calculate real compatibility scores based on group ratings
        compatibility_scores = {}
        for movie in movies:
            # Get all ratings for this movie from group members
            movie_ratings = db.query(Rating).filter(
                Rating.movie_id == movie.id,
                Rating.user_id.in_(user_ids)
            ).all()
            
            if movie_ratings:
                # Calculate average rating and convert to compatibility score
                avg_rating = sum(r.rating for r in movie_ratings) / len(movie_ratings)
                # Convert 1-5 rating to 0-1 compatibility score
                compatibility = (avg_rating - 1) / 4
                compatibility_scores[movie.id] = round(max(0.1, min(1.0, compatibility)), 2)
            else:
                # Default compatibility for unrated movies
                compatibility_scores[movie.id] = round(random.uniform(0.5, 0.8), 2)
        
        return WatchPartyResponse(
            movies=movies,
            compatibility_scores=compatibility_scores
        )
    except Exception as e:
        logger.error(f"Error getting watch party recommendations: {str(e)}")
        # Fallback with random scores
        movies = get_watch_party_recommendations(db, request.user_ids, 10)
        compatibility_scores = {movie.id: round(random.uniform(0.7, 1.0), 2) for movie in movies}
        return WatchPartyResponse(
            movies=movies,
            compatibility_scores=compatibility_scores
        )


@router.post("/retrain")
async def retrain_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger model retraining
    Useful when new data is added or models need updating
    """
    try:
        logger.info(f"Manual model retraining triggered by user {current_user.id}")
        initialize_recommendation_model(db, force_retrain=True)
        
        # Get model metadata
        models_info = ModelPersistence.list_saved_models()
        
        return {
            "status": "success",
            "message": "Models retrained successfully",
            "models": models_info
        }
    except Exception as e:
        logger.error(f"Error retraining models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrain models: {str(e)}"
        )


@router.get("/models/status")
async def get_models_status(current_user: User = Depends(get_current_user)):
    """Get status of saved models"""
    try:
        models_info = ModelPersistence.list_saved_models()
        
        return {
            "status": "success",
            "models_loaded": models_loaded,
            "saved_models": models_info
        }
    except Exception as e:
        logger.error(f"Error getting models status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models status: {str(e)}"
        )


@router.post("/refresh")
async def refresh_recommendations(
    current_user: User = Depends(get_current_user)
):
    """
    Clear user's recommendation history to get fresh recommendations
    """
    global user_recommended_movies
    
    try:
        if current_user.id in user_recommended_movies:
            count = len(user_recommended_movies[current_user.id])
            user_recommended_movies[current_user.id].clear()
            logger.info(f"Cleared {count} recommendations for user {current_user.id}")
            
            return {
                "status": "success",
                "message": f"Cleared {count} previous recommendations. You'll now see fresh suggestions!",
                "cleared_count": count
            }
        else:
            return {
                "status": "success",
                "message": "No previous recommendations to clear",
                "cleared_count": 0
            }
    except Exception as e:
        logger.error(f"Error refreshing recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh recommendations: {str(e)}"
        )