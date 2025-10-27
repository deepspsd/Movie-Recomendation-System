from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Movie, Rating
from schemas import MovieResponse, SearchResponse, SearchParams
from services.tmdb_service import TMDBService, get_tmdb_movies_data, search_tmdb_movies, get_tmdb_movie_details
from utils.cache import cached, cache_movie_details
from typing import List, Optional
import logging
import asyncio
import json

router = APIRouter(prefix="/movies", tags=["Movies"])

logger = logging.getLogger(__name__)


@router.get("/", response_model=SearchResponse)
async def get_all_movies(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get all movies with pagination
    """
    try:
        offset = (page - 1) * limit
        movies = db.query(Movie).offset(offset).limit(limit).all()
        total_count = db.query(Movie).count()
        
        return SearchResponse(
            movies=movies,
            total_results=total_count,
            total_pages=(total_count + limit - 1) // limit,
            page=page
        )
    except Exception as e:
        logger.error(f"Error fetching movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trending", response_model=List[MovieResponse])
async def get_trending_movies(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get trending movies
    """
    try:
        movies = db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()
        return movies
    except Exception as e:
        logger.error(f"Error fetching trending movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/popular", response_model=List[MovieResponse])
async def get_popular_movies(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get popular movies
    """
    try:
        movies = db.query(Movie).order_by(Movie.vote_average.desc()).limit(limit).all()
        return movies
    except Exception as e:
        logger.error(f"Error fetching popular movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=SearchResponse)
async def search_movies(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "popularity",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search movies with filters
    """
    try:
        offset = (page - 1) * limit
        query_obj = db.query(Movie)
        
        # Apply filters
        if query:
            query_obj = query_obj.filter(Movie.title.contains(query))
        
        if genre:
            query_obj = query_obj.filter(Movie.genres.contains(genre))
        
        if year:
            query_obj = query_obj.filter(Movie.release_date.contains(year))
        
        if min_rating:
            query_obj = query_obj.filter(Movie.vote_average >= min_rating)
        
        # Apply sorting
        if sort_by == "rating":
            query_obj = query_obj.order_by(Movie.vote_average.desc())
        elif sort_by == "release_date":
            query_obj = query_obj.order_by(Movie.release_date.desc())
        else:
            query_obj = query_obj.order_by(Movie.popularity.desc())
        
        # Apply pagination
        movies = query_obj.offset(offset).limit(limit).all()
        total_count = query_obj.count()
        
        return SearchResponse(
            movies=movies,
            total_results=total_count,
            total_pages=(total_count + limit - 1) // limit,
            page=page
        )
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tmdb/search", response_model=List[MovieResponse])
async def search_tmdb_live(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search movies directly from TMDB API (live search)
    """
    try:
        # Search TMDB directly
        tmdb_movies = await search_tmdb_movies(query, limit)
        
        if not tmdb_movies:
            return []
        
        # Convert to our format and save to database
        movies = []
        for tmdb_movie in tmdb_movies:
            # Check if movie exists in our DB
            existing_movie = db.query(Movie).filter(Movie.id == tmdb_movie["id"]).first()
            
            if existing_movie:
                movies.append(existing_movie)
            else:
                # Create new movie from TMDB data
                new_movie = Movie(
                    id=tmdb_movie["id"],
                    title=tmdb_movie["title"],
                    overview=tmdb_movie["overview"],
                    poster_path=tmdb_movie["poster_path"],
                    backdrop_path=tmdb_movie["backdrop_path"],
                    release_date=tmdb_movie["release_date"],
                    vote_average=tmdb_movie["vote_average"],
                    vote_count=tmdb_movie["vote_count"],
                    popularity=tmdb_movie["popularity"],
                    genres=json.dumps(tmdb_movie.get("genres", []))
                )
                db.add(new_movie)
                db.commit()
                db.refresh(new_movie)
                movies.append(new_movie)
        
        return movies
        
    except Exception as e:
        logger.error(f"Error searching TMDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tmdb/popular", response_model=List[MovieResponse])
async def get_tmdb_popular(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get popular movies from TMDB API
    """
    try:
        async with TMDBService() as tmdb:
            tmdb_movies = await tmdb.get_popular_movies(limit=limit)
            
            if not tmdb_movies:
                return []
            
            movies = []
            for tmdb_movie in tmdb_movies:
                # Check if movie exists in our DB
                existing_movie = db.query(Movie).filter(Movie.id == tmdb_movie["id"]).first()
                
                if existing_movie:
                    movies.append(existing_movie)
                else:
                    # Create new movie from TMDB data
                    formatted_movie = tmdb.format_movie_data(tmdb_movie)
                    new_movie = Movie(
                        id=formatted_movie["id"],
                        title=formatted_movie["title"],
                        overview=formatted_movie["overview"],
                        poster_path=formatted_movie["poster_path"],
                        backdrop_path=formatted_movie["backdrop_path"],
                        release_date=formatted_movie["release_date"],
                        vote_average=formatted_movie["vote_average"],
                        vote_count=formatted_movie["vote_count"],
                        popularity=formatted_movie["popularity"],
                        genres=json.dumps(formatted_movie.get("genres", []))
                    )
                    db.add(new_movie)
                    db.commit()
                    db.refresh(new_movie)
                    movies.append(new_movie)
            
            return movies
            
    except Exception as e:
        logger.error(f"Error getting TMDB popular movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """
    Get movie details by ID with enhanced data from TMDB
    """
    try:
        # First check local database
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if not movie:
            # If not in local DB, try to get from TMDB
            try:
                tmdb_movie = await get_tmdb_movie_details(movie_id)
                if tmdb_movie:
                    # Save to local database for future use
                    new_movie = Movie(
                        id=tmdb_movie["id"],
                        title=tmdb_movie["title"],
                        overview=tmdb_movie["overview"],
                        poster_path=tmdb_movie["poster_path"],
                        backdrop_path=tmdb_movie["backdrop_path"],
                        release_date=tmdb_movie["release_date"],
                        vote_average=tmdb_movie["vote_average"],
                        vote_count=tmdb_movie["vote_count"],
                        popularity=tmdb_movie["popularity"],
                        genres=json.dumps(tmdb_movie.get("genres", []))
                    )
                    db.add(new_movie)
                    db.commit()
                    db.refresh(new_movie)
                    movie = new_movie
                else:
                    raise HTTPException(status_code=404, detail="Movie not found")
            except Exception as tmdb_error:
                logger.error(f"Error fetching from TMDB: {str(tmdb_error)}")
                raise HTTPException(status_code=404, detail="Movie not found")
        
        return movie
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie {movie_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")