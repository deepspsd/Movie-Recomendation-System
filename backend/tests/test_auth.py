"""
Authentication API Tests
Uses the actual cloud database for testing
"""

import pytest
import os
from fastapi.testclient import TestClient
from main import app
from database import get_db_context
from models import User

# Set testing environment
os.environ['TESTING'] = 'true'

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    """Clean up test data before and after each test"""
    # Clean up before test
    with get_db_context() as db:
        # Delete test users
        db.query(User).filter(User.email.like('%@example.com')).delete()
        db.commit()
    
    yield
    
    # Clean up after test
    with get_db_context() as db:
        # Delete test users
        db.query(User).filter(User.email.like('%@example.com')).delete()
        db.commit()

def test_register_user(setup_database):
    """Test user registration"""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"

def test_register_duplicate_email(setup_database):
    """Test registration with duplicate email"""
    # First registration
    client.post("/api/auth/register", json={
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "Password123"
    })
    
    # Second registration with same email
    response = client.post("/api/auth/register", json={
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "Password123"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_user(setup_database):
    """Test user login"""
    # Register user first
    client.post("/api/auth/register", json={
        "username": "logintest",
        "email": "login@example.com",
        "password": "Password123"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data

def test_login_invalid_credentials(setup_database):
    """Test login with invalid credentials"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_get_current_user(setup_database):
    """Test getting current user info"""
    # Register and login
    register_response = client.post("/api/auth/register", json={
        "username": "currentuser",
        "email": "current@example.com",
        "password": "Password123"
    })
    token = register_response.json()["access_token"]
    
    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"