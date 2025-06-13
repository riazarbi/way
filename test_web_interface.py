#!/usr/bin/env python3
"""
Web interface test for AI Hypothesis Evaluation System
Tests the Flask web application endpoints and form submission.
"""

import sys
import os
import threading
import time
import requests

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def start_test_server():
    """Start Flask app in test mode."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.run(host='127.0.0.1', port=5001, use_reloader=False)

def test_web_interface():
    """Test web interface endpoints."""
    print("=" * 60)
    print("WEB INTERFACE VALIDATION TESTS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5001"
    
    # Start server in background
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Starting test server on port 5001...")
    time.sleep(3)
    
    try:
        # Test 1: Homepage GET request
        print("\nTest 1: Homepage Access")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        homepage_checks = [
            (response.status_code == 200, "HTTP 200 response"),
            ("AI Hypothesis Evaluation System" in response.text, "Contains page title"),
            ('<form method="POST"' in response.text, "Contains form"),
            ('name="hypothesis"' in response.text, "Contains hypothesis input"),
            ('type="submit"' in response.text, "Contains submit button"),
            ("Evaluation Results:" in response.text, "Contains results area")
        ]
        
        for check, description in homepage_checks:
            print(f"{'✅' if check else '❌'} {description}")
        
        # Test 2: Health endpoint
        print("\nTest 2: Health Endpoint")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status code: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Health status: {health_data.get('status', 'unknown')}")
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
        
        # Test 3: Form submission
        print("\nTest 3: Hypothesis Form Submission")
        test_hypothesis = "Due to low conversion rates, if we improve the checkout process, then users will complete more purchases, measured by a 15% increase in conversion rate"
        
        form_data = {"hypothesis": test_hypothesis}
        post_response = requests.post(f"{base_url}/", data=form_data, timeout=10)
        
        print(f"Status code: {post_response.status_code}")
        print(f"Response length: {len(post_response.text)}")
        
        form_checks = [
            (post_response.status_code == 200, "HTTP 200 response"),
            ("Score:" in post_response.text, "Contains evaluation score"),
            ("Strengths:" in post_response.text, "Contains strengths section"),
            ("Weaknesses:" in post_response.text, "Contains weaknesses section"),
            ("Improvements:" in post_response.text, "Contains improvements section"),
            (test_hypothesis in post_response.text, "Preserves submitted hypothesis")
        ]
        
        for check, description in form_checks:
            print(f"{'✅' if check else '❌'} {description}")
        
        # Test 4: Empty form submission
        print("\nTest 4: Empty Form Submission")
        empty_form_data = {"hypothesis": ""}
        empty_response = requests.post(f"{base_url}/", data=empty_form_data, timeout=5)
        
        empty_checks = [
            (empty_response.status_code == 200, "HTTP 200 response"),
            ("Error" in empty_response.text or "Please enter" in empty_response.text, "Shows error message"),
            ("⚠️" in empty_response.text, "Contains warning icon")
        ]
        
        for check, description in empty_checks:
            print(f"{'✅' if check else '❌'} {description}")
        
        # Test 5: 404 error handling
        print("\nTest 5: 404 Error Handling")
        not_found_response = requests.get(f"{base_url}/nonexistent", timeout=5)
        print(f"Status code: {not_found_response.status_code}")
        
        if not_found_response.status_code == 404:
            print("✅ 404 handling working")
        else:
            print("❌ 404 handling failed")
        
        print("\n" + "=" * 60)
        print("WEB INTERFACE TESTS COMPLETED")
        print("=" * 60)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_web_interface()
    sys.exit(0 if success else 1)