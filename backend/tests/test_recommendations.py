"""
Recommendations API Tests
Uses the actual cloud database for testing
"""

import pytest
import os
from fastapi.testclient import TestClient
from database import get_db_context
from models import Movie, User, Rating
from main import app
import json
from datetime import datetime

# Set testing environment
os.environ['TESTING'] = 'true'

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    """Setup and cleanup test data"""
    # Clean up before test
    with get_db_context() as db:
        db.query(User).filter(User.email.like('%@example.com')).delete()
        db.query(Movie).filter(Movie.id.in_([1, 2, 3])).delete()
        db.query(Rating).filter(Rating.user_id == "test_user_1").delete()
        db.commit()
    
    yield
    
    # Clean up after test
    with get_db_context() as db:
        db.query(User).filter(User.email.like('%@example.com')).delete()
        db.query(Movie).filter(Movie.id.in_([1, 2, 3])).delete()
        db.query(Rating).filter(Rating.user_id == "test_user_1").delete()
        db.commit()

def test_get_personalized_recommendations(setup_database):
    """Test getting personalized recommendations"""
    # Register and login user
    register_response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123"
    })
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/recommendations/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert "algorithm" in data
    assert len(data["movies"]) > 0

def test_get_mood_recommendations(setup_database):
    """Test getting mood-based recommendations"""
    # Register and login user
    register_response = client.post("/api/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "Password123"
    })
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/recommendations/mood?mood=happy", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert "algorithm" in data
    assert data["algorithm"] == "mood_based"

def test_get_similar_movies(setup_database):
    """Test getting similar movies"""
    response = client.get("/api/recommendations/similar/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_watch_party_recommendations(setup_database):
    """Test getting watch party recommendations"""
    # Register and login user
    register_response = client.post("/api/auth/register", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "Password123"
    })
    token = register_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/recommendations/group", 
                          json={"user_ids": ["test_user_1"]}, 
                          headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert "compatibility_scores" in data
