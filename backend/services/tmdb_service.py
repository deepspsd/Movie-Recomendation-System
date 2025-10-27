"""
Movie API Service - Supports both TMDB and OMDb APIs
TMDB: Free API for movie data (preferred)
OMDb: Alternative free API (fallback)
"""

import httpx
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TMDBService:
    """
    Service for interacting with TMDB or OMDb API
    TMDB: 1000 requests/day, 40 requests per 10 seconds
    OMDb: 1000 requests/day (free tier)
    """
    
    def __init__(self):
        # TMDB configuration
        self.tmdb_api_key = os.getenv("TMDB_API_KEY")
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        
        # OMDb configuration
        self.omdb_api_key = os.getenv("OMDB_API_KEY")
        self.omdb_base_url = "http://www.omdbapi.com/"
        
        # Determine which API to use
        self.use_omdb = bool(self.omdb_api_key) and not bool(self.tmdb_api_key)
        self.api_key = self.omdb_api_key if self.use_omdb else self.tmdb_api_key
        self.base_url = self.omdb_base_url if self.use_omdb else self.tmdb_base_url
        
        self.session = None
        
        if self.use_omdb:
            logger.info("Using OMDb API for movie data")
        elif self.tmdb_api_key:
            logger.info("Using TMDB API for movie data")
        else:
            logger.warning("No movie API key configured. Using sample data only.")
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to TMDB API with error handling"""
        if not self.session:
            self.session = httpx.AsyncClient()
            
        try:
            url = f"{self.base_url}{endpoint}"
            request_params = {"api_key": self.api_key}
            if params:
                request_params.update(params)
            
            response = await self.session.get(url, params=request_params)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"TMDB API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error making TMDB request: {str(e)}")
            return None
    
    async def get_popular_movies(self, page: int = 1, limit: int = 20) -> List[Dict]:
        """Get popular movies from TMDB"""
        try:
            data = await self._make_request("/movie/popular", {"page": page})
            if not data:
                return []
            
            movies = data.get("results", [])
            return movies[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []
    
    async def get_trending_movies(self, time_window: str = "week", limit: int = 20) -> List[Dict]:
        """Get trending movies from TMDB"""
        try:
            data = await self._make_request(f"/trending/movie/{time_window}")
            if not data:
                return []
            
            movies = data.get("results", [])
            return movies[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {str(e)}")
            return []
    
    async def get_top_rated_movies(self, page: int = 1, limit: int = 20) -> List[Dict]:
        """Get top rated movies from TMDB"""
        try:
            data = await self._make_request("/movie/top_rated", {"page": page})
            if not data:
                return []
            
            movies = data.get("results", [])
            return movies[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top rated movies: {str(e)}")
            return []
    
    async def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a specific movie"""
        try:
            data = await self._make_request(f"/movie/{movie_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting movie details for {movie_id}: {str(e)}")
            return None
    
    async def get_movie_credits(self, movie_id: int) -> Optional[Dict]:
        """Get cast and crew information for a movie"""
        try:
            data = await self._make_request(f"/movie/{movie_id}/credits")
            return data
            
        except Exception as e:
            logger.error(f"Error getting movie credits for {movie_id}: {str(e)}")
            return None
    
    async def get_movie_videos(self, movie_id: int) -> Optional[Dict]:
        """Get videos (trailers, clips) for a movie"""
        try:
            data = await self._make_request(f"/movie/{movie_id}/videos")
            return data
            
        except Exception as e:
            logger.error(f"Error getting movie videos for {movie_id}: {str(e)}")
            return None
    
    async def search_movies(self, query: str, page: int = 1, limit: int = 20) -> List[Dict]:
        """Search for movies by title"""
        try:
            data = await self._make_request("/search/movie", {
                "query": query,
                "page": page,
                "include_adult": False
            })
            if not data:
                return []
            
            movies = data.get("results", [])
            return movies[:limit]
            
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []
    
    async def get_movies_by_genre(self, genre_id: int, page: int = 1, limit: int = 20) -> List[Dict]:
        """Get movies by genre"""
        try:
            data = await self._make_request("/discover/movie", {
                "with_genres": genre_id,
                "page": page,
                "sort_by": "popularity.desc"
            })
            if not data:
                return []
            
            movies = data.get("results", [])
            return movies[:limit]
            
        except Exception as e:
            logger.error(f"Error getting movies by genre {genre_id}: {str(e)}")
            return []
    
    async def get_genres(self) -> List[Dict]:
        """Get list of movie genres"""
        try:
            data = await self._make_request("/genre/movie/list")
            if not data:
                return []
            
            return data.get("genres", [])
            
        except Exception as e:
            logger.error(f"Error getting genres: {str(e)}")
            return []
    
    def get_image_url(self, path: str, size: str = "w500") -> str:
        """Get full image URL from TMDB path"""
        if not path or path == "N/A":
            return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&h=750&fit=crop"
        
        # If already a full URL (from OMDb), return as-is
        if path.startswith("http://") or path.startswith("https://"):
            return path
            
        # TMDB path format
        return f"{self.image_base_url}/{size}{path}"
    
    def get_backdrop_url(self, path: str, size: str = "original") -> str:
        """Get full backdrop URL from TMDB path"""
        if not path or path == "N/A":
            return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920&h=1080&fit=crop"
        
        # If already a full URL (from OMDb), return as-is
        if path.startswith("http://") or path.startswith("https://"):
            return path
            
        # TMDB path format
        return f"{self.image_base_url}/{size}{path}"
    
    def format_movie_data(self, tmdb_movie: Dict) -> Dict:
        """Format TMDB movie data for our database"""
        return {
            "id": tmdb_movie.get("id"),
            "title": tmdb_movie.get("title"),
            "overview": tmdb_movie.get("overview"),
            "poster_path": tmdb_movie.get("poster_path"),
            "backdrop_path": tmdb_movie.get("backdrop_path"),
            "release_date": tmdb_movie.get("release_date"),
            "vote_average": tmdb_movie.get("vote_average"),
            "vote_count": tmdb_movie.get("vote_count"),
            "popularity": tmdb_movie.get("popularity"),
            "genres": tmdb_movie.get("genre_ids", []),
            "adult": tmdb_movie.get("adult", False),
            "original_language": tmdb_movie.get("original_language"),
            "original_title": tmdb_movie.get("original_title")
        }


# Global instance
tmdb_service = TMDBService()


async def get_tmdb_movies_data(limit: int = 100) -> List[Dict]:
    """
    Get comprehensive movie data from TMDB
    Combines popular, trending, and top-rated movies
    """
    async with TMDBService() as tmdb:
        all_movies = []
        
        try:
            # Get movies from different categories
            popular = await tmdb.get_popular_movies(page=1, limit=limit//3)
            trending = await tmdb.get_trending_movies(limit=limit//3)
            top_rated = await tmdb.get_top_rated_movies(page=1, limit=limit//3)
            
            # Combine and deduplicate
            movie_ids = set()
            for movie_list in [popular, trending, top_rated]:
                for movie in movie_list:
                    if movie.get("id") not in movie_ids:
                        all_movies.append(tmdb.format_movie_data(movie))
                        movie_ids.add(movie.get("id"))
            
            logger.info(f"Retrieved {len(all_movies)} unique movies from TMDB")
            return all_movies
            
        except Exception as e:
            logger.error(f"Error getting TMDB movies data: {str(e)}")
            return []


async def search_tmdb_movies(query: str, limit: int = 20) -> List[Dict]:
    """Search movies on TMDB"""
    async with TMDBService() as tmdb:
        try:
            movies = await tmdb.search_movies(query, limit=limit)
            return [tmdb.format_movie_data(movie) for movie in movies]
        except Exception as e:
            logger.error(f"Error searching TMDB movies: {str(e)}")
            return []


async def get_tmdb_movie_details(movie_id: int) -> Optional[Dict]:
    """Get detailed movie information from TMDB"""
    async with TMDBService() as tmdb:
        try:
            movie_data = await tmdb.get_movie_details(movie_id)
            if not movie_data:
                return None
            
            # Get additional data
            credits = await tmdb.get_movie_credits(movie_id)
            videos = await tmdb.get_movie_videos(movie_id)
            
            # Combine data
            detailed_movie = tmdb.format_movie_data(movie_data)
            
            if credits:
                detailed_movie["cast"] = credits.get("cast", [])[:10]  # Top 10 cast
                detailed_movie["crew"] = credits.get("crew", [])[:5]   # Top 5 crew
            
            if videos:
                # Find trailer
                trailer = None
                for video in videos.get("results", []):
                    if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                        trailer = video
                        break
                detailed_movie["trailer"] = trailer
            
            return detailed_movie
            
        except Exception as e:
            logger.error(f"Error getting TMDB movie details for {movie_id}: {str(e)}")
            return None
