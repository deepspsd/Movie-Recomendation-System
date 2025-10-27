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
import random
import json
import logging
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
logger = logging.getLogger(__name__)

# Global recommendation model instances
recommendation_model = None
content_model = None
hybrid_model = None
evaluator = None
models_loaded = False


def get_popular_movies(db: Session, limit: int = 20) -> List[Movie]:
    """Get popular movies based on vote count and average rating"""
    return db.query(Movie).filter(
        Movie.vote_count >= 100,
        Movie.vote_average >= 6.0
    ).order_by(Movie.popularity.desc()).limit(limit).all()


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
    """Get mood-based recommendations"""
    mood_genres = {
        "happy": ["comedy", "family", "animation", "music"],
        "sad": ["drama", "romance"],
        "adventurous": ["action", "adventure", "thriller", "fantasy"],
        "romantic": ["romance", "comedy"],
        "scared": ["horror", "thriller", "mystery"],
        "thoughtful": ["drama", "documentary", "sci-fi"]
    }
    
    genres = mood_genres.get(mood.lower(), ["drama"])
    
    # For mini project, we'll just get popular movies
    return get_popular_movies(db, limit)


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
        # Try to load models from disk first
        if not force_retrain and not models_loaded:
            logger.info("Attempting to load models from disk...")
            
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


def get_advanced_recommendations(db: Session, user_id: str, algorithm: str = "hybrid", limit: int = 10) -> List[Movie]:
    """Get advanced recommendations using ML algorithms"""
    global recommendation_model, content_model, hybrid_model
    
    try:
        # Initialize models if not done
        if recommendation_model is None or content_model is None or hybrid_model is None:
            initialize_recommendation_model(db)
        
        if recommendation_model is None:
            return get_popular_movies(db, limit)
        
        # Get recommendations based on algorithm
        if algorithm == "hybrid":
            # Use advanced hybrid recommender with adaptive weighting
            recommendations = hybrid_model.get_hybrid_recommendations(user_id, limit, use_adaptive=True)
        elif algorithm == "als":
            # Use ALS collaborative filtering
            recommendations = recommendation_model.get_als_recommendations(user_id, limit)
        elif algorithm == "svd":
            recommendations = recommendation_model.get_svd_recommendations(user_id, limit)
        elif algorithm == "collaborative":
            recommendations = recommendation_model.get_user_recommendations(user_id, limit)
        elif algorithm == "content":
            # Get user's highly rated movies for content-based
            user_ratings = db.query(Rating).filter(
                Rating.user_id == user_id,
                Rating.rating >= 4.0
            ).all()
            liked_movies = [r.movie_id for r in user_ratings]
            recommendations = content_model.get_recommendations_for_user(liked_movies, limit)
        else:
            # Default to hybrid
            recommendations = hybrid_model.get_hybrid_recommendations(user_id, limit, use_adaptive=True)
        
        if not recommendations:
            return get_popular_movies(db, limit)
        
        # Get movie objects
        movie_ids = [movie_id for movie_id, _ in recommendations]
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        
        # Sort by recommendation score
        movie_dict = {movie.id: movie for movie in movies}
        sorted_movies = []
        for movie_id, score in recommendations:
            if movie_id in movie_dict:
                sorted_movies.append(movie_dict[movie_id])
        
        return sorted_movies[:limit]
        
    except Exception as e:
        logger.error(f"Error getting advanced recommendations: {str(e)}")
        return get_popular_movies(db, limit)


@router.get("/", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized movie recommendations for the current user
    """
    try:
        # Get advanced recommendations using ML algorithms
        movies = get_advanced_recommendations(db, current_user.id, "hybrid", 10)
        
        return RecommendationResponse(
            movies=movies,
            algorithm="hybrid",
            explanation="Personalized recommendations using collaborative filtering and matrix factorization"
        )
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {str(e)}")
        # Fallback to popular movies
        movies = get_popular_movies(db, 10)
        return RecommendationResponse(
            movies=movies,
            algorithm="popular",
            explanation="Popular movies (fallback)"
        )


@router.get("/mood", response_model=RecommendationResponse)
async def get_mood_recommendations_endpoint(
    mood: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get movie recommendations based on user's mood
    """
    try:
        # Get mood-based recommendations
        movies = get_mood_recommendations(db, mood, 10)
        
        # If we have user data, try to personalize based on mood
        if current_user:
            # Get user's favorite genres and combine with mood
            favorite_genres = []
            if current_user.favorite_genres:
                try:
                    favorite_genres = json.loads(current_user.favorite_genres)
                except:
                    favorite_genres = []
            
            # Filter movies by mood and user preferences
            if favorite_genres:
                mood_movies = [m for m in movies if any(genre in str(m.genres).lower() for genre in favorite_genres)]
                if mood_movies:
                    movies = mood_movies
        
        return RecommendationResponse(
            movies=movies,
            algorithm="mood_based",
            explanation=f"Movies that match your {mood} mood and preferences"
        )
    except Exception as e:
        logger.error(f"Error getting mood recommendations: {str(e)}")
        movies = get_mood_recommendations(db, mood, 10)
        return RecommendationResponse(
            movies=movies,
            algorithm="mood_based",
            explanation=f"Movies that match your {mood} mood"
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