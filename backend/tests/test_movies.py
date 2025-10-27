"""
Movies API Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
from models import Movie, User
from main import app
import json

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    # Create test movies
    db = TestingSessionLocal()
    test_movies = [
        Movie(
            id=1,
            title="The Shawshank Redemption",
            overview="Two imprisoned men bond over a number of years...",
            poster_path="/poster1.jpg",
            backdrop_path="/backdrop1.jpg",
            release_date="1994-09-23",
            vote_average=9.3,
            vote_count=10000,
            popularity=85.5,
            genres=json.dumps([{"id": 18, "name": "Drama"}])
        ),
        Movie(
            id=2,
            title="The Godfather",
            overview="The aging patriarch of an organized crime dynasty...",
            poster_path="/poster2.jpg",
            backdrop_path="/backdrop2.jpg",
            release_date="1972-03-24",
            vote_average=9.2,
            vote_count=8000,
            popularity=90.2,
            genres=json.dumps([{"id": 80, "name": "Crime"}, {"id": 18, "name": "Drama"}])
        )
    ]
    
    for movie in test_movies:
        db.add(movie)
    db.commit()
    db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_all_movies(setup_database):
    """Test getting all movies"""
    response = client.get("/api/movies/")
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert len(data["movies"]) == 2
    assert data["total_results"] == 2

def test_get_movie_by_id(setup_database):
    """Test getting movie by ID"""
    response = client.get("/api/movies/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "The Shawshank Redemption"

def test_get_movie_not_found(setup_database):
    """Test getting non-existent movie"""
    response = client.get("/api/movies/999")
    assert response.status_code == 404

def test_search_movies(setup_database):
    """Test searching movies"""
    response = client.get("/api/movies/search?query=Shawshank")
    assert response.status_code == 200
    data = response.json()
    assert len(data["movies"]) == 1
    assert data["movies"][0]["title"] == "The Shawshank Redemption"

def test_search_movies_by_genre(setup_database):
    """Test searching movies by genre"""
    response = client.get("/api/movies/search?genre=Drama")
    assert response.status_code == 200
    data = response.json()
    assert len(data["movies"]) == 2  # Both movies have Drama genre

def test_get_trending_movies(setup_database):
    """Test getting trending movies"""
    response = client.get("/api/movies/trending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_popular_movies(setup_database):
    """Test getting popular movies"""
    response = client.get("/api/movies/popular")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
