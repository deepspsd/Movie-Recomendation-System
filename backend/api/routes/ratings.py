from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Rating, Movie, User
from schemas import RatingCreate, RatingResponse, RatingRequest
from utils.auth_middleware import get_current_user
from typing import List
import uuid
import logging
from datetime import datetime, timezone

router = APIRouter(prefix="/ratings", tags=["Ratings"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new rating for a movie
    """
    try:
        # Check if movie exists
        movie = db.query(Movie).filter(Movie.id == rating_data.movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        user_id = current_user.id
        
        # Check if rating already exists
        existing_rating = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == rating_data.movie_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_data.rating
            existing_rating.timestamp = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_rating)
            return existing_rating
        else:
            # Create new rating
            rating_id = str(uuid.uuid4())
            new_rating = Rating(
                id=rating_id,
                user_id=user_id,
                movie_id=rating_data.movie_id,
                rating=rating_data.rating
            )
            
            db.add(new_rating)
            db.commit()
            db.refresh(new_rating)
            return new_rating
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rating: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user", response_model=List[RatingResponse])
async def get_user_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all ratings for the current user
    """
    try:
        user_id = current_user.id
        ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        return ratings
    except Exception as e:
        logger.error(f"Error fetching user ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/movie/{movie_id}", response_model=RatingResponse)
async def get_movie_rating(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get rating for a specific movie by the current user
    """
    try:
        user_id = current_user.id
        
        rating = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        ).first()
        
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
            
        return rating
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie rating: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")