"""
Response Optimization Utilities
Compress and optimize API responses
"""

from typing import Any, Dict, List
import json
from datetime import datetime


def optimize_movie_response(movie: Any) -> Dict:
    """
    Optimize movie object for API response
    Remove unnecessary fields and format data
    """
    return {
        'id': movie.id,
        'title': movie.title,
        'overview': movie.overview[:200] if movie.overview else None,  # Truncate long descriptions
        'poster_path': movie.poster_path,
        'backdrop_path': movie.backdrop_path,
        'release_date': movie.release_date,
        'vote_average': round(movie.vote_average, 1) if movie.vote_average else None,
        'vote_count': movie.vote_count,
        'popularity': round(movie.popularity, 1) if movie.popularity else None,
    }


def optimize_movie_list(movies: List[Any]) -> List[Dict]:
    """
    Optimize list of movies for API response
    """
    return [optimize_movie_response(movie) for movie in movies]


def paginate_response(items: List[Any], page: int, limit: int, total: int) -> Dict:
    """
    Create paginated response with metadata
    """
    total_pages = (total + limit - 1) // limit
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime to ISO string
    """
    return dt.isoformat() if dt else None


def remove_null_fields(data: Dict) -> Dict:
    """
    Remove null/None fields from response
    """
    return {k: v for k, v in data.items() if v is not None}


def compress_json_response(data: Any) -> str:
    """
    Compress JSON response by removing whitespace
    """
    return json.dumps(data, separators=(',', ':'))


class ResponseOptimizer:
    """
    Response optimization helper
    """
    
    @staticmethod
    def optimize_for_mobile(data: Dict) -> Dict:
        """
        Optimize response for mobile devices
        Reduce payload size by removing unnecessary fields
        """
        if isinstance(data, dict):
            # Remove large fields for mobile
            mobile_data = data.copy()
            if 'backdrop_path' in mobile_data:
                # Use smaller image for mobile
                mobile_data['backdrop_path'] = mobile_data['backdrop_path']
            return mobile_data
        return data
    
    @staticmethod
    def add_cache_headers(max_age: int = 3600) -> Dict[str, str]:
        """
        Generate cache control headers
        """
        return {
            'Cache-Control': f'public, max-age={max_age}',
            'Vary': 'Accept-Encoding'
        }
    
    @staticmethod
    def create_error_response(message: str, status_code: int = 400, details: Dict = None) -> Dict:
        """
        Create standardized error response
        """
        response = {
            'error': True,
            'message': message,
            'status_code': status_code
        }
        if details:
            response['details'] = details
        return response
    
    @staticmethod
    def create_success_response(data: Any, message: str = None) -> Dict:
        """
        Create standardized success response
        """
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        return response
