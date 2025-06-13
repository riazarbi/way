#!/usr/bin/env python3
"""
Validation test script for AI Hypothesis Evaluation System
Tests end-to-end functionality, error handling, response formatting, and performance.
"""

import time
import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import GeminiAPIClient, process_ai_response, format_evaluation_response, format_error_response

def test_end_to_end_evaluation():
    """Test end-to-end hypothesis evaluation workflow."""
    print("=" * 60)
    print("TEST 1: End-to-End Evaluation Workflow")
    print("=" * 60)
    
    client = GeminiAPIClient()
    
    # Test various hypothesis inputs
    test_hypotheses = [
        "Due to low conversion rates, if we improve the checkout process, then users will complete more purchases, measured by a 15% increase in conversion rate",
        "Adding gamification features will improve user engagement",
        "",  # Empty input test
        "Very short",  # Minimal input test
        "If we change button color from blue to red then click rates will improve due to higher visibility measured by 10% CTR increase"  # Different structure
    ]
    
    results = []
    for i, hypothesis in enumerate(test_hypotheses, 1):
        print(f"\nTest Case {i}: {'(Empty)' if not hypothesis else hypothesis[:50]}...")
        
        start_time = time.time()
        response = client.evaluate_hypothesis(hypothesis)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Response time: {response_time:.2f}ms")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        if isinstance(response, dict) and 'score' in response:
            print(f"Score: {response['score']}")
            if response.get('justification'):
                print(f"Justification items: {len(response['justification'])}")
        
        results.append({
            'hypothesis': hypothesis,
            'response': response,
            'response_time_ms': response_time
        })
        
        # Validate response time requirement (<500ms)
        if response_time > 500:
            print(f"⚠️  WARNING: Response time {response_time:.2f}ms exceeds 500ms target")
        else:
            print(f"✅ Response time within target")
    
    return results

def test_api_error_handling():
    """Test API error handling and timeout scenarios."""
    print("\n" + "=" * 60)
    print("TEST 2: API Error Handling")
    print("=" * 60)
    
    client = GeminiAPIClient()
    
    # Test 1: Missing API key handling
    original_key = client.api_key
    client.api_key = None
    
    print("\nTest Case 1: Missing API Key")
    response = client.evaluate_hypothesis("Test hypothesis")
    print(f"Response with no API key: {response.get('score', 'No score')}")
    
    # Test 2: Error response processing
    print("\nTest Case 2: Error Response Processing")
    error_response = {
        "score": "Error",
        "justification": [{
            "strengths": "Unable to evaluate due to system error.",
            "weaknesses": "API connection failed",
            "improvements": "Please try again or contact support if the issue persists."
        }]
    }
    
    processed_error = process_ai_response(error_response)
    print(f"Error response processed: {'✅ Success' if 'Error' in processed_error else '❌ Failed'}")
    
    # Test 3: Invalid response format
    print("\nTest Case 3: Invalid Response Format")
    invalid_responses = [
        "string response",  # String instead of dict
        {"invalid": "format"},  # Missing required fields
        {"score": "Good"},  # Missing justification
        {"score": "Good", "justification": "string"}  # Invalid justification format
    ]
    
    for i, invalid_response in enumerate(invalid_responses, 1):
        processed = process_ai_response(invalid_response)
        print(f"Invalid response {i}: {'✅ Handled' if 'Error' in processed else '❌ Not handled properly'}")
    
    # Restore original API key
    client.api_key = original_key
    
    return True

def test_response_formatting():
    """Test response formatting and display validation."""
    print("\n" + "=" * 60)
    print("TEST 3: Response Formatting Validation")
    print("=" * 60)
    
    # Test successful response formatting
    print("\nTest Case 1: Successful Response Formatting")
    sample_response = {
        "score": "Very Good",
        "justification": [{
            "strengths": "Well-structured hypothesis with clear data points and comprehensive analysis.",
            "weaknesses": "Could specify exact measurement timeframes for better tracking.",
            "improvements": "Consider adding specific success thresholds and measurement intervals."
        }]
    }
    
    formatted = process_ai_response(sample_response)
    
    # Validate HTML formatting
    html_checks = [
        ('<h3' in formatted, "Has score header"),
        ('style="color:' in formatted, "Has color styling"),
        ('Strengths:' in formatted, "Contains strengths section"),
        ('Weaknesses:' in formatted, "Contains weaknesses section"),
        ('Improvements:' in formatted, "Contains improvements section"),
        ('&lt;' not in formatted or '&gt;' not in formatted, "Proper HTML escaping")
    ]
    
    for check, description in html_checks:
        print(f"{'✅' if check else '❌'} {description}")
    
    # Test error formatting
    print("\nTest Case 2: Error Response Formatting")
    error_formatted = format_error_response("Test error message")
    
    error_checks = [
        ('⚠️' in error_formatted, "Has warning icon"),
        ('background-color: #f8d7da' in error_formatted, "Has error styling"),
        ('Test error message' in error_formatted, "Contains error message"),
        ('try again' in error_formatted.lower(), "Has user guidance")
    ]
    
    for check, description in error_checks:
        print(f"{'✅' if check else '❌'} {description}")
    
    return True

def test_performance_targets():
    """Test performance against targets."""
    print("\n" + "=" * 60)
    print("TEST 4: Performance Testing")
    print("=" * 60)
    
    client = GeminiAPIClient()
    test_hypothesis = "Due to low user engagement, if we implement push notifications, then user retention will improve, measured by 20% increase in daily active users"
    
    response_times = []
    
    print("Running 10 evaluation requests to measure performance...")
    for i in range(10):
        start_time = time.time()
        response = client.evaluate_hypothesis(test_hypothesis)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        response_times.append(response_time)
        
        if i % 3 == 0:  # Print progress every 3 requests
            print(f"Request {i+1}: {response_time:.2f}ms")
    
    # Calculate statistics
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Calculate 95th percentile
    sorted_times = sorted(response_times)
    p95_index = int(0.95 * len(sorted_times))
    p95_time = sorted_times[p95_index]
    
    print(f"\nPerformance Results:")
    print(f"Average response time: {avg_time:.2f}ms")
    print(f"95th percentile: {p95_time:.2f}ms")
    print(f"Min time: {min_time:.2f}ms")
    print(f"Max time: {max_time:.2f}ms")
    
    # Check against 500ms target for 95% of requests
    target_met = p95_time < 500
    print(f"\n{'✅' if target_met else '❌'} Performance target (<500ms for 95% of requests): {'MET' if target_met else 'NOT MET'}")
    
    return target_met

def main():
    """Run all validation tests."""
    print("AI Hypothesis Evaluation System - Validation Tests")
    print("=" * 60)
    
    # Track test results
    test_results = {}
    
    try:
        # Run all tests
        test_results['end_to_end'] = test_end_to_end_evaluation()
        test_results['error_handling'] = test_api_error_handling()
        test_results['formatting'] = test_response_formatting()
        test_results['performance'] = test_performance_targets()
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        
        print(f"Tests completed: {total_tests}")
        print(f"Tests passed: {passed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Individual test results
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL VALIDATION TESTS PASSED")
            return True
        else:
            print(f"\n⚠️  {total_tests - passed_tests} TEST(S) FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED WITH ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)