"""Debug registration test"""
import os
os.environ['TESTING'] = 'true'

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

response = client.post("/api/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123"
})

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
