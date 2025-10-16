#!/usr/bin/env python
"""
Test script for JWT authentication.
Run this to verify JWT authentication is working correctly.
"""

import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv('API_URL', 'http://localhost:4000')
PASSWORD = os.getenv('EDITOR_PASSWORD', '')

def test_jwt_auth():
    """Test JWT authentication flow."""
    print("Testing JWT Authentication Flow")
    print("=" * 50)
    
    # Test 1: Check auth without token (should fail if password is set)
    print("\n1. Testing authentication check without token...")
    response = requests.get(f"{BASE_URL}/api/auth/check")
    if PASSWORD:
        if response.status_code == 401:
            print("✅ Correctly denied access without token")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    else:
        if response.status_code == 200:
            print("✅ No password set - access allowed")
        else:
            print(f"❌ Expected 200 (no password), got {response.status_code}")
    
    # Test 2: Login with password
    if PASSWORD:
        print("\n2. Testing login with password...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"password": PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                token = data['token']
                print(f"✅ Login successful, token received: {token[:20]}...")
            else:
                print("❌ Login successful but no token in response")
                return
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        # Test 3: Check auth with token
        print("\n3. Testing authentication check with token...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/check", headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully authenticated with JWT token")
        else:
            print(f"❌ Authentication failed with token: {response.status_code}")
        
        # Test 4: Test protected endpoint
        print("\n4. Testing protected endpoint with token...")
        test_data = {
            "content_type": "MCQ",
            "generator_model": "gemini",
            "input_text": "Test input text for authentication testing.",
            "num_questions": 1,
            "focus_areas": None
        }
        
        response = requests.post(
            f"{BASE_URL}/run",
            json=test_data,
            headers=headers
        )
        
        if response.status_code in [200, 422, 500]:  # Any response other than 401
            print(f"✅ Protected endpoint accessible with token (status: {response.status_code})")
        else:
            print(f"❌ Protected endpoint denied access: {response.status_code}")
        
        # Test 5: Test without token should fail
        print("\n5. Testing protected endpoint without token...")
        response = requests.post(f"{BASE_URL}/run", json=test_data)
        
        if response.status_code == 401:
            print("✅ Correctly denied access without token")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    else:
        print("\nNo password set - skipping authentication tests")
    
    print("\n" + "=" * 50)
    print("JWT Authentication Test Complete")

if __name__ == "__main__":
    try:
        test_jwt_auth()
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
