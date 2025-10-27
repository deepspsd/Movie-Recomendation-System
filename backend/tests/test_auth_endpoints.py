"""
Test script to verify authentication endpoints are working correctly
Run this after starting the backend server
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "password": "Test123456"
}

def print_response(response, title):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        print_response(response, "Health Check")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("🔍 Testing Registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Registration")
        
        if response.status_code == 201:
            data = response.json()
            if "access_token" in data and "user" in data:
                print("✅ Registration successful!")
                return data["access_token"]
            else:
                print("❌ Registration response missing required fields")
                return None
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login():
    """Test user login"""
    print("🔍 Testing Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Login")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                print("✅ Login successful!")
                return data["access_token"]
            else:
                print("❌ Login response missing required fields")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("🔍 Testing Get Current User...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        print_response(response, "Get Current User")
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data:
                print("✅ Get current user successful!")
                return True
            else:
                print("❌ User response missing required fields")
                return False
        else:
            print(f"❌ Get current user failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        return False

def test_duplicate_registration():
    """Test duplicate registration handling"""
    print("🔍 Testing Duplicate Registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Duplicate Registration")
        
        if response.status_code == 400:
            print("✅ Duplicate registration correctly rejected!")
            return True
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Duplicate registration test error: {e}")
        return False

def test_invalid_login():
    """Test invalid login credentials"""
    print("🔍 Testing Invalid Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": "WrongPassword123"
            },
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Invalid Login")
        
        if response.status_code == 401:
            print("✅ Invalid login correctly rejected!")
            return True
        else:
            print(f"❌ Expected 401 status, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 AUTHENTICATION ENDPOINTS TEST SUITE")
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Health Check
    if test_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Backend server may not be running. Start it with: python main.py")
        return
    
    # Test 2: Registration
    token = test_registration()
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Registration failed. Check database connection and logs.")
        return
    
    # Test 3: Get Current User
    if test_get_current_user(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Login
    login_token = test_login()
    if login_token:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Duplicate Registration
    if test_duplicate_registration():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 6: Invalid Login
    if test_invalid_login():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Success Rate: {(results['passed']/(results['passed']+results['failed'])*100):.1f}%")
    print("="*60 + "\n")
    
    if results["failed"] == 0:
        print("🎉 All tests passed! Authentication is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
