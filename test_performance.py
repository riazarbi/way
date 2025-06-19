#!/usr/bin/env python3
"""
Performance testing script for hypothesis feedback tool.
Tests response times and validates sub-200ms requirement.
"""
import time
import statistics
import concurrent.futures
from app.ollama_client import OllamaClient


def test_single_request(client, hypothesis):
    """Test a single hypothesis analysis request."""
    start_time = time.time()
    result = client.analyze_hypothesis(hypothesis)
    end_time = time.time()
    
    response_time_ms = (end_time - start_time) * 1000
    success = result is not None and 'error' not in result
    
    return {
        'response_time_ms': response_time_ms,
        'success': success,
        'result': result
    }


def run_performance_test():
    """Run comprehensive performance test."""
    print("Starting performance test...")
    
    client = OllamaClient()
    
    # Test hypotheses of varying complexity
    test_hypotheses = [
        "If we change the button color from blue to green, conversion will increase by 5%.",
        "If we add social proof testimonials to the landing page, then user trust will increase and signup rate will improve by 10% because social validation reduces uncertainty.",
        "Making the site better will help users.",
        "If we reduce the checkout steps from 5 to 3, then cart abandonment will decrease by 15% because fewer steps reduce friction.",
        "Adding a progress bar to the signup process will improve completion rates."
    ]
    
    # Warm up the model
    print("Warming up model...")
    warmup_result = client.warm_up()
    print(f"Warm-up {'successful' if warmup_result else 'failed'}")
    
    # Single request test
    print("\n--- Single Request Performance Test ---")
    results = []
    
    for i, hypothesis in enumerate(test_hypotheses):
        print(f"Testing hypothesis {i+1}/5...")
        result = test_single_request(client, hypothesis)
        results.append(result)
        print(f"  Response time: {result['response_time_ms']:.2f}ms, Success: {result['success']}")
    
    # Calculate statistics
    response_times = [r['response_time_ms'] for r in results if r['success']]
    success_rate = sum(1 for r in results if r['success']) / len(results) * 100
    
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        sub_200ms_count = sum(1 for t in response_times if t < 200)
        sub_200ms_percentage = (sub_200ms_count / len(response_times)) * 100
        
        print(f"\n--- Single Request Results ---")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Median response time: {median_time:.2f}ms")
        print(f"Min response time: {min_time:.2f}ms")
        print(f"Max response time: {max_time:.2f}ms")
        print(f"Sub-200ms requests: {sub_200ms_count}/{len(response_times)} ({sub_200ms_percentage:.1f}%)")
        print(f"Performance target met: {'✅ YES' if sub_200ms_percentage >= 95 else '❌ NO'}")
    
    # Concurrent request test
    print(f"\n--- Concurrent Request Performance Test ---")
    concurrent_results = []
    
    def concurrent_test():
        return test_single_request(client, test_hypotheses[0])
    
    # Test with 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        start_time = time.time()
        futures = [executor.submit(concurrent_test) for _ in range(5)]
        concurrent_results = [future.result() for future in concurrent_futures.as_completed(futures)]
        total_time = time.time() - start_time
    
    concurrent_response_times = [r['response_time_ms'] for r in concurrent_results if r['success']]
    concurrent_success_rate = sum(1 for r in concurrent_results if r['success']) / len(concurrent_results) * 100
    
    if concurrent_response_times:
        concurrent_avg = statistics.mean(concurrent_response_times)
        concurrent_sub_200ms = sum(1 for t in concurrent_response_times if t < 200)
        concurrent_sub_200ms_percentage = (concurrent_sub_200ms / len(concurrent_response_times)) * 100
        
        print(f"Total test time: {total_time:.2f}s")
        print(f"Success rate: {concurrent_success_rate:.1f}%")
        print(f"Average response time: {concurrent_avg:.2f}ms")
        print(f"Sub-200ms requests: {concurrent_sub_200ms}/{len(concurrent_response_times)} ({concurrent_sub_200ms_percentage:.1f}%)")
        print(f"Concurrent performance target met: {'✅ YES' if concurrent_sub_200ms_percentage >= 95 else '❌ NO'}")
    
    # Get client performance metrics
    print(f"\n--- Client Performance Metrics ---")
    metrics = client.get_performance_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    return {
        'single_request': {
            'success_rate': success_rate,
            'avg_response_time_ms': avg_time if response_times else 0,
            'sub_200ms_percentage': sub_200ms_percentage if response_times else 0
        },
        'concurrent_request': {
            'success_rate': concurrent_success_rate,
            'avg_response_time_ms': concurrent_avg if concurrent_response_times else 0,
            'sub_200ms_percentage': concurrent_sub_200ms_percentage if concurrent_response_times else 0
        }
    }


if __name__ == "__main__":
    test_results = run_performance_test()
    
    # Final validation
    print("\n" + "="*50)
    print("PERFORMANCE VALIDATION SUMMARY")
    print("="*50)
    
    single_passed = test_results['single_request']['sub_200ms_percentage'] >= 95
    concurrent_passed = test_results['concurrent_request']['sub_200ms_percentage'] >= 95
    
    print(f"Single request test: {'✅ PASSED' if single_passed else '❌ FAILED'}")
    print(f"Concurrent request test: {'✅ PASSED' if concurrent_passed else '❌ FAILED'}")
    print(f"Overall performance optimization: {'✅ SUCCESS' if single_passed and concurrent_passed else '❌ NEEDS IMPROVEMENT'}")