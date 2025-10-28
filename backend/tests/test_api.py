"""Quick API test script"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing Movie Recommendation System API...")
print("=" * 60)

# Test 1: Root endpoint
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"\n1. Root endpoint: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: API info
try:
    r = requests.get(f"{BASE_URL}/api")
    print(f"\n2. API info: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Movies endpoint
try:
    r = requests.get(f"{BASE_URL}/api/movies/popular")
    print(f"\n3. Popular movies: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Found {len(data)} movies")
        if data:
            print(f"   First movie: {data[0].get('title', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Check if we need authentication
try:
    r = requests.get(f"{BASE_URL}/api/recommendations")
    print(f"\n4. Recommendations (no auth): {r.status_code}")
    if r.status_code == 401:
        print("   Authentication required (expected)")
    elif r.status_code == 200:
        data = r.json()
        print(f"   Success! Found {len(data.get('movies', []))} recommendations")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("API Test Complete!")
