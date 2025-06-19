#!/usr/bin/env python3
"""
Simple test script for HTTP API endpoints.
Run this after starting the Flask application to validate functionality.
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the HTTP API endpoints."""
    base_url = "http://localhost:5000"
    
    print("Testing Hypothesis Feedback Tool API")
    print("=" * 40)
    
    # Test 1: API Health Check
    print("\n1. Testing API Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ API Health Check passed")
    except Exception as e:
        print(f"❌ API Health Check failed: {e}")
    
    # Test 2: Valid Hypothesis Submission
    print("\n2. Testing Valid Hypothesis Submission...")
    valid_data = {
        "hypothesis": "Changing the button color from blue to green will increase click-through rate by 15%",
        "experiment_type": "a_b_test",
        "metrics": ["click_through_rate", "conversion_rate"]
    }
    try:
        response = requests.post(
            f"{base_url}/api/hypothesis",
            json=valid_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 201
        print("✅ Valid Hypothesis Submission passed")
    except Exception as e:
        print(f"❌ Valid Hypothesis Submission failed: {e}")
    
    # Test 3: Invalid Hypothesis Submission (missing fields)
    print("\n3. Testing Invalid Hypothesis Submission...")
    invalid_data = {
        "hypothesis": "Short"  # Missing required fields and too short
    }
    try:
        response = requests.post(
            f"{base_url}/api/hypothesis",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ Invalid Hypothesis Submission handled correctly")
    except Exception as e:
        print(f"❌ Invalid Hypothesis Submission test failed: {e}")
    
    # Test 4: Wrong Content Type
    print("\n4. Testing Wrong Content Type...")
    try:
        response = requests.post(
            f"{base_url}/api/hypothesis",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ Wrong Content Type handled correctly")
    except Exception as e:
        print(f"❌ Wrong Content Type test failed: {e}")
    
    # Test 5: Performance Check
    print("\n5. Testing Response Performance...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/health")
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        print(f"Response time: {response_time:.2f}ms")
        assert response_time < 50  # Should be under 50ms as per requirements
        print("✅ Performance requirement met")
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    
    print("\n" + "=" * 40)
    print("API testing completed!")

if __name__ == "__main__":
    test_api_endpoints()