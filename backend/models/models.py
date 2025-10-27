from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Index
from datetime import datetime, timezone
from database import Base

# Handle case where Base is None (e.g., during testing or database connection issues)
if Base is None:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string for MySQL
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    favorite_genres = Column(Text, nullable=True)  # Store as JSON string
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Movie(Base):
    """Movie model for storing movie information from TMDB"""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)  # TMDB movie ID
    title = Column(String(255), nullable=False, index=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String(255), nullable=True)
    backdrop_path = Column(String(255), nullable=True)
    release_date = Column(String(20), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    popularity = Column(Float, nullable=True)
    genres = Column(Text, nullable=True)  # Store as JSON string
    runtime = Column(Integer, nullable=True)
    tagline = Column(String(500), nullable=True)
    
    # Advanced metadata fields for hybrid recommendation
    director = Column(String(255), nullable=True)  # Director name
    cast = Column(Text, nullable=True)  # JSON array of cast members
    keywords = Column(Text, nullable=True)  # JSON array of keywords
    budget = Column(Float, nullable=True)  # Movie budget
    revenue = Column(Float, nullable=True)  # Movie revenue
    director_score = Column(Float, default=0.0)  # Director reputation score
    actor_score = Column(Float, default=0.0)  # Average actor popularity score
    budget_revenue_ratio = Column(Float, default=0.0)  # Revenue/Budget ratio
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title={self.title})>"


class Rating(Base):
    """Rating model for user movie ratings"""
    __tablename__ = "ratings"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Composite index for faster queries
    __table_args__ = (
        Index('idx_user_movie', 'user_id', 'movie_id'),
    )
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"


class Watchlist(Base):
    """Watchlist model for user's saved movies"""
    __tablename__ = "watchlist"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Composite index and unique constraint
    __table_args__ = (
        Index('idx_user_movie_watchlist', 'user_id', 'movie_id', unique=True),
    )
    
    def __repr__(self):
        return f"<Watchlist(user_id={self.user_id}, movie_id={self.movie_id})>"


class Review(Base):
    """Review model for user movie reviews (optional)"""
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    review_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<Review(user_id={self.user_id}, movie_id={self.movie_id})>"