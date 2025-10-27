from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Watchlist, Movie, User
from schemas import WatchlistCreate, WatchlistResponse
from utils.auth_middleware import get_current_user
from typing import List
import uuid
import logging
from datetime import datetime

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

logger = logging.getLogger(__name__)


@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all movies in the user's watchlist
    """
    try:
        user_id = current_user.id
        watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
        return watchlist_items
    except Exception as e:
        logger.error(f"Error fetching watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a movie to the user's watchlist
    """
    try:
        user_id = current_user.id
        
        # Check if movie exists
        movie = db.query(Movie).filter(Movie.id == watchlist_data.movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Check if movie is already in watchlist
        existing_item = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == watchlist_data.movie_id
        ).first()
        
        if existing_item:
            raise HTTPException(status_code=400, detail="Movie already in watchlist")
        
        # Add to watchlist
        watchlist_id = str(uuid.uuid4())
        new_item = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            movie_id=watchlist_data.movie_id
        )
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a movie from the user's watchlist
    """
    try:
        user_id = current_user.id
        
        # Find item in watchlist
        item = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Movie not in watchlist")
        
        db.delete(item)
        db.commit()
        return
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/check/{movie_id}", response_model=dict)
async def check_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a movie is in the user's watchlist
    """
    try:
        user_id = current_user.id
        
        # Check if movie is in watchlist
        item = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id
        ).first()
        
        return {"in_watchlist": item is not None}
        
    except Exception as e:
        logger.error(f"Error checking watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")