from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    favorite_genres: Optional[List[str]] = []

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    favorite_genres: Optional[List[str]] = None


# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


# Rating Schemas
class RatingCreate(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=1.0, le=5.0)


class RatingRequest(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=1.0, le=5.0)


class RatingResponse(BaseModel):
    id: str
    user_id: str
    movie_id: int
    rating: float
    timestamp: datetime

    model_config = {"from_attributes": True}


# Watchlist Schemas
class WatchlistCreate(BaseModel):
    movie_id: int


class WatchlistResponse(BaseModel):
    id: str
    user_id: str
    movie_id: int
    added_at: datetime

    model_config = {"from_attributes": True}


# Movie Schemas
class MovieBase(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None


class MovieResponse(MovieBase):
    genres: Optional[List[dict]] = []
    runtime: Optional[int] = None
    tagline: Optional[str] = None

    model_config = {"from_attributes": True}
    
    @field_validator('genres', mode='before')
    @classmethod
    def parse_genres(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    movies: List[MovieResponse]
    algorithm: str
    explanation: Optional[str] = None


# Search Schemas
class SearchParams(BaseModel):
    query: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[str] = None
    min_rating: Optional[float] = None
    sort_by: Optional[str] = "popularity"
    page: Optional[int] = 1


class SearchResponse(BaseModel):
    movies: List[MovieResponse]
    total_results: int
    total_pages: int
    page: int

    model_config = {"from_attributes": True}


# Error Response
class ErrorResponse(BaseModel):
    detail: str
    status_code: int


# Success Response
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None


# Mood Recommendation Request
class MoodRecommendationRequest(BaseModel):
    mood: str


# Watch Party Request
class WatchPartyRequest(BaseModel):
    user_ids: List[str]


# Watch Party Response
class WatchPartyResponse(BaseModel):
    movies: List[MovieResponse]
    compatibility_scores: Dict[int, float]
