"""Test registration endpoint directly"""
import requests
import json

url = "http://localhost:8000/api/auth/register"

data = {
    "username": "testuser123",
    "email": "testuser123@example.com",
    "password": "Password123"
}

print(f"Testing registration at: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to backend!")
    print("Make sure backend is running: python main.py")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
