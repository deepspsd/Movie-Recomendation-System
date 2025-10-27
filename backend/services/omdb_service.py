"""
OMDB API Service
Fetches movie data from OMDB API including posters, trailers, and detailed information
"""

import os
import requests
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

class OMDBService:
    def __init__(self):
        # Extract just the API key from the URL format in .env
        omdb_url = os.getenv("OMDB_API_KEY", "")
        if "apikey=" in omdb_url:
            self.api_key = omdb_url.split("apikey=")[1]
        else:
            self.api_key = omdb_url
        
        self.base_url = "http://www.omdbapi.com/"
        
        # In-memory cache for movie data
        self._cache = {}
        self._cache_timestamp = {}
        
        # Best movies in the world (IMDb IDs)
        self.best_movies = [
            "tt0111161",  # The Shawshank Redemption
            "tt0068646",  # The Godfather
            "tt0468569",  # The Dark Knight
            "tt0071562",  # The Godfather Part II
            "tt0050083",  # 12 Angry Men
            "tt0108052",  # Schindler's List
            "tt0167260",  # The Lord of the Rings: The Return of the King
            "tt0110912",  # Pulp Fiction
            "tt0120737",  # The Lord of the Rings: The Fellowship of the Ring
            "tt0060196",  # The Good, the Bad and the Ugly
            "tt0109830",  # Forrest Gump
            "tt0137523",  # Fight Club
            "tt0167261",  # The Lord of the Rings: The Two Towers
            "tt0080684",  # Star Wars: Episode V - The Empire Strikes Back
            "tt1375666",  # Inception
            "tt0073486",  # One Flew Over the Cuckoo's Nest
            "tt0099685",  # Goodfellas
            "tt0133093",  # The Matrix
            "tt0047478",  # Seven Samurai
            "tt0114369",  # Se7en
            "tt0317248",  # City of God
            "tt0076759",  # Star Wars: Episode IV - A New Hope
            "tt0102926",  # The Silence of the Lambs
            "tt0038650",  # It's a Wonderful Life
            "tt0118799",  # Life Is Beautiful
            "tt0245429",  # Spirited Away
            "tt0120815",  # Saving Private Ryan
            "tt0816692",  # Interstellar
            "tt6751668",  # Parasite
            "tt0114814",  # The Usual Suspects
            "tt0120689",  # The Green Mile
            "tt0103064",  # Terminator 2: Judgment Day
            "tt0047396",  # Rear Window
            "tt0054215",  # Psycho
            "tt0110413",  # Léon: The Professional
            "tt0120586",  # American History X
            "tt0034583",  # Casablanca
            "tt0021749",  # City Lights
            "tt0064116",  # Once Upon a Time in the West
            "tt0027977",  # Modern Times
            "tt0253474",  # The Pianist
            "tt0407887",  # The Departed
            "tt0088763",  # Back to the Future
            "tt0482571",  # The Prestige
            "tt0078788",  # Apocalypse Now
            "tt0078748",  # Alien
            "tt0209144",  # Memento
            "tt0095327",  # Grave of the Fireflies
            "tt0043014",  # Sunset Boulevard
            "tt0082971",  # Raiders of the Lost Ark
        ]
        
        # Popular recent movies (30+ movies)
        self.popular_movies = [
            "tt15398776", # Oppenheimer
            "tt1517268",  # Barbie
            "tt6710474",  # Everything Everywhere All at Once
            "tt9362722",  # Spider-Man: Across the Spider-Verse
            "tt10366206", # John Wick: Chapter 4
            "tt9419884",  # Doctor Strange in the Multiverse of Madness
            "tt10872600", # Spider-Man: No Way Home
            "tt1160419",  # Dune
            "tt8041270",  # Killers of the Flower Moon
            "tt14230458", # Poor Things
            "tt4154796",  # Avengers: Endgame
            "tt4633694",  # Spider-Man: Into the Spider-Verse
            "tt7286456",  # Joker
            "tt8503618",  # Hamilton
            "tt1745960",  # Top Gun: Maverick
            "tt9114286",  # Black Panther: Wakanda Forever
            "tt11138512", # The Whale
            "tt10648342", # Thor: Love and Thunder
            "tt9603212",  # Guardians of the Galaxy Vol. 3
            "tt6467266",  # Babylon
            "tt1877830",  # The Batman
            "tt10954600", # Ant-Man and the Wasp: Quantumania
            "tt5113044",  # The Northman
            "tt1464335",  # Uncharted
            "tt11145118", # The Menu
            "tt14444726", # Tár
            "tt10298810", # The Fabelmans
            "tt1649418",  # Cocaine Bear
            "tt13320622", # M3GAN
            "tt15791034", # Scream VI
            "tt11564570", # Glass Onion: A Knives Out Mystery
            "tt1745960",  # Elvis
            "tt13320622", # Avatar: The Way of Water
            "tt9114286",  # The Woman King
            "tt12412888", # Nope
        ]

    def get_movie_by_id(self, imdb_id: str, retries: int = 3) -> Optional[Dict]:
        """Fetch detailed movie information by IMDb ID with retry logic and caching"""
        # Check cache first (cache for 1 hour)
        cache_key = f"movie_{imdb_id}"
        if cache_key in self._cache:
            cache_age = time.time() - self._cache_timestamp.get(cache_key, 0)
            if cache_age < 3600:  # 1 hour
                logger.debug(f"Cache hit for {imdb_id}")
                return self._cache[cache_key]
        
        for attempt in range(retries):
            try:
                params = {
                    "apikey": self.api_key,
                    "i": imdb_id,
                    "plot": "full"
                }
                
                response = requests.get(self.base_url, params=params, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("Response") == "True":
                    formatted_data = self._format_movie_data(data)
                    # Cache the result
                    self._cache[cache_key] = formatted_data
                    self._cache_timestamp[cache_key] = time.time()
                    return formatted_data
                else:
                    logger.warning(f"Movie not found: {imdb_id}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching movie {imdb_id}, attempt {attempt + 1}/{retries}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch movie {imdb_id} after {retries} attempts")
                    return None
                time.sleep(0.5)  # Wait 0.5 second before retry (reduced from 1s)
                continue
            except Exception as e:
                logger.error(f"Error fetching movie {imdb_id}: {str(e)}")
                return None
        
        return None

    def search_movies(self, query: str, page: int = 1) -> Dict:
        """Search for movies by title"""
        try:
            params = {
                "apikey": self.api_key,
                "s": query,
                "type": "movie",
                "page": page
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Response") == "True":
                movies = []
                for item in data.get("Search", []):
                    # Fetch full details for each movie
                    movie_details = self.get_movie_by_id(item["imdbID"])
                    if movie_details:
                        movies.append(movie_details)
                
                return {
                    "movies": movies,
                    "total_results": int(data.get("totalResults", 0)),
                    "page": page
                }
            else:
                return {"movies": [], "total_results": 0, "page": page}
                
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return {"movies": [], "total_results": 0, "page": page}

    def get_best_movies(self, limit: int = 50) -> List[Dict]:
        """Get the best movies in the world (IMDb Top 250) with caching"""
        cache_key = f"best_movies_{limit}"
        
        # Check cache (cache for 6 hours)
        if cache_key in self._cache:
            cache_age = time.time() - self._cache_timestamp.get(cache_key, 0)
            if cache_age < 21600:  # 6 hours
                logger.info(f"[CACHE HIT] Returning cached best movies ({len(self._cache[cache_key])} movies)")
                return self._cache[cache_key]
        
        logger.info(f"[FETCHING] Getting {limit} best movies from OMDb...")
        movies = []
        
        for i, imdb_id in enumerate(self.best_movies[:limit]):
            movie = self.get_movie_by_id(imdb_id)  # This uses its own cache
            if movie:
                movies.append(movie)
            else:
                logger.warning(f"Skipping movie {imdb_id} due to fetch failure")
            
            # NO DELAY - rely on individual movie cache instead
        
        logger.info(f"[SUCCESS] Fetched {len(movies)} out of {limit} movies")
        
        # Cache the result
        self._cache[cache_key] = movies
        self._cache_timestamp[cache_key] = time.time()
        
        return movies

    def get_popular_movies(self, limit: int = 20) -> List[Dict]:
        """Get popular recent movies with caching"""
        cache_key = f"popular_movies_{limit}"
        
        # Check cache (cache for 1 hour)
        if cache_key in self._cache:
            cache_age = time.time() - self._cache_timestamp.get(cache_key, 0)
            if cache_age < 3600:  # 1 hour
                logger.info(f"[CACHE HIT] Returning cached popular movies ({len(self._cache[cache_key])} movies)")
                return self._cache[cache_key]
        
        logger.info(f"[FETCHING] Getting {limit} popular movies from OMDb...")
        movies = []
        
        for i, imdb_id in enumerate(self.popular_movies[:limit]):
            movie = self.get_movie_by_id(imdb_id)  # This uses its own cache
            if movie:
                movies.append(movie)
            else:
                logger.warning(f"Skipping movie {imdb_id} due to fetch failure")
            
            # NO DELAY - rely on individual movie cache instead
        
        logger.info(f"[SUCCESS] Fetched {len(movies)} out of {limit} popular movies")
        
        # Cache the result
        self._cache[cache_key] = movies
        self._cache_timestamp[cache_key] = time.time()
        
        return movies

    def get_movies_by_year(self, year: int, limit: int = 20) -> List[Dict]:
        """Get top movies from a specific year"""
        try:
            # Search for movies from that year
            params = {
                "apikey": self.api_key,
                "s": "movie",  # Generic search
                "type": "movie",
                "y": year
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("Response") == "True":
                movies = []
                for item in data.get("Search", [])[:limit]:
                    movie = self.get_movie_by_id(item["imdbID"])
                    if movie:
                        movies.append(movie)
                return movies
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching movies by year: {str(e)}")
            return []

    def _format_movie_data(self, data: Dict) -> Dict:
        """Format OMDB data to match our Movie model"""
        try:
            # Parse genres
            genres = []
            if data.get("Genre"):
                genre_names = data["Genre"].split(", ")
                genres = [{"id": i + 1, "name": name} for i, name in enumerate(genre_names)]
            
            # Parse cast
            cast = []
            if data.get("Actors"):
                actor_names = data["Actors"].split(", ")
                cast = [{"id": i + 1, "name": name, "character": "", "profile_path": None} 
                       for i, name in enumerate(actor_names)]
            
            # Parse ratings
            imdb_rating = float(data.get("imdbRating", "0") or "0")
            
            # Convert IMDb ID to numeric ID (remove 'tt' prefix and convert)
            imdb_id = data.get("imdbID", "tt0000000")
            numeric_id = int(imdb_id.replace("tt", "")) if imdb_id.startswith("tt") else 0
            
            # Parse release date to YYYY-MM-DD format
            release_date = data.get("Released", "")
            if release_date and release_date != "N/A":
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(release_date, "%d %b %Y")
                    release_date = date_obj.strftime("%Y-%m-%d")
                except:
                    release_date = data.get("Year", "") + "-01-01"
            else:
                release_date = data.get("Year", "") + "-01-01"
            
            # Parse runtime
            runtime = 0
            if data.get("Runtime") and data.get("Runtime") != "N/A":
                try:
                    runtime = int(data.get("Runtime", "0").split()[0])
                except:
                    runtime = 0
            
            return {
                "id": numeric_id,
                "title": data.get("Title", "Unknown"),
                "overview": data.get("Plot", "No description available.") if data.get("Plot") != "N/A" else "No description available.",
                "poster_path": data.get("Poster", "") if data.get("Poster") != "N/A" else None,
                "backdrop_path": data.get("Poster", "") if data.get("Poster") != "N/A" else None,
                "release_date": release_date,
                "vote_average": imdb_rating,
                "vote_count": int(data.get("imdbVotes", "0").replace(",", "") or "0"),
                "popularity": imdb_rating * 10,
                "genres": genres,
                "runtime": runtime,
                "tagline": data.get("Plot", "")[:100] if data.get("Plot") and data.get("Plot") != "N/A" else "",
                "director": data.get("Director", "Unknown") if data.get("Director") != "N/A" else "Unknown",
                "cast": cast,
                "trailer_key": None,
                "keywords": data.get("Genre", "").split(", ") if data.get("Genre") != "N/A" else [],
                "budget": 0,
                "revenue": 0,
                "imdb_rating": imdb_rating,
                "imdb_id": imdb_id,
                "year": data.get("Year", ""),
                "rated": data.get("Rated", "") if data.get("Rated") != "N/A" else "",
                "awards": data.get("Awards", "") if data.get("Awards") != "N/A" else "",
                "box_office": data.get("BoxOffice", "") if data.get("BoxOffice") != "N/A" else "",
                "production": data.get("Production", "") if data.get("Production") != "N/A" else "",
                "website": data.get("Website", "") if data.get("Website") != "N/A" else "",
            }
        except Exception as e:
            logger.error(f"Error formatting movie data: {str(e)}")
            return {}


# Singleton instance
omdb_service = OMDBService()
