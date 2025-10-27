"""
OMDB API Routes
Endpoints for fetching movies from OMDB API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.omdb_service import omdb_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/omdb", tags=["OMDB Movies"])


@router.get("/best-movies")
async def get_best_movies(limit: int = Query(50, ge=1, le=50)):
    """
    Get the best movies in the world (IMDb Top 250)
    """
    try:
        movies = omdb_service.get_best_movies(limit=limit)
        return {
            "success": True,
            "movies": movies,
            "count": len(movies)
        }
    except Exception as e:
        logger.error(f"Error fetching best movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch best movies")


@router.get("/popular")
async def get_popular_movies(limit: int = Query(30, ge=1, le=50)):
    """
    Get popular recent movies
    """
    try:
        movies = omdb_service.get_popular_movies(limit=limit)
        return {
            "success": True,
            "movies": movies,
            "count": len(movies)
        }
    except Exception as e:
        logger.error(f"Error fetching popular movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch popular movies")


@router.get("/search")
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1)
):
    """
    Search for movies by title
    """
    try:
        result = omdb_service.search_movies(query=query, page=page)
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search movies")


@router.get("/movie/{imdb_id}")
async def get_movie_details(imdb_id: str):
    """
    Get detailed information about a specific movie by IMDb ID
    """
    try:
        movie = omdb_service.get_movie_by_id(imdb_id)
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        return {
            "success": True,
            "movie": movie
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch movie details")


@router.get("/by-year/{year}")
async def get_movies_by_year(
    year: int,
    limit: int = Query(30, ge=1, le=50)
):
    """
    Get top movies from a specific year
    """
    try:
        # Validate year range
        if year < 1900 or year > 2025:
            raise HTTPException(status_code=400, detail="Year must be between 1900 and 2025")
        
        movies = omdb_service.get_movies_by_year(year=year, limit=limit)
        return {
            "success": True,
            "movies": movies,
            "year": year,
            "count": len(movies)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movies by year: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch movies by year")
