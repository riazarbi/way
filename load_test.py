#!/usr/bin/env python3
"""Focused WebSocket Load Testing for Hypothesis Feedback Tool"""

import asyncio
import time
import statistics
import socketio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TestResult:
    response_time: float
    success: bool
    cache_hit: bool = False
    error: str = ""


class LoadTester:
    """WebSocket load testing framework"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.hypotheses = [
            "Users prefer blue buttons over red buttons for conversion",
            "Shorter headlines increase click-through rates", 
            "Free shipping messaging reduces cart abandonment",
            "Social proof badges increase trust and conversions",
            "Personalized recommendations increase average order value"
        ]
    
    def _run_client(self, client_id: int, num_requests: int) -> List[TestResult]:
        """Run load test for single client"""
        sio = socketio.Client()
        results = []
        
        try:
            sio.connect(self.base_url)
            
            for i in range(num_requests):
                start_time = time.time()
                response_data = {}
                response_event = threading.Event()
                
                @sio.on('analysis_result')
                def on_result(data):
                    response_data.update(data)
                    response_event.set()
                
                @sio.on('error')
                def on_error(data):
                    response_data['error'] = str(data)
                    response_event.set()
                
                hypothesis = self.hypotheses[i % len(self.hypotheses)]
                sio.emit('analyze_hypothesis', {'hypothesis': hypothesis})
                
                if response_event.wait(timeout=3.0):
                    response_time = time.time() - start_time
                    if 'error' in response_data:
                        results.append(TestResult(response_time, False, error=response_data['error']))
                    else:
                        cache_hit = response_data.get('cache_hit', False)
                        results.append(TestResult(response_time, True, cache_hit=cache_hit))
                else:
                    results.append(TestResult(time.time() - start_time, False, error="Timeout"))
                
                time.sleep(0.1)  # Small delay between requests
                
        except Exception as e:
            results.append(TestResult(0, False, error=str(e)))
        finally:
            try:
                sio.disconnect()
            except:
                pass
        
        return results
    
    def run_load_test(self, num_clients: int, requests_per_client: int) -> Dict[str, Any]:
        """Execute concurrent load test"""
        print(f"Running load test: {num_clients} clients, {requests_per_client} requests each")
        start_time = time.time()
        all_results = []
        
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(self._run_client, i, requests_per_client) 
                      for i in range(num_clients)]
            
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"Client failed: {e}")
        
        total_time = time.time() - start_time
        return self._analyze_results(all_results, total_time, num_clients)
    
    def _analyze_results(self, results: List[TestResult], total_time: float, num_clients: int) -> Dict[str, Any]:
        """Analyze test results"""
        successful = [r for r in results if r.success]
        
        if not successful:
            return {
                'total_requests': len(results),
                'success_rate': 0,
                'avg_response_time': 0,
                'targets_met': False,
                'error': 'All requests failed'
            }
        
        response_times = [r.response_time for r in successful]
        cache_hits = sum(1 for r in successful if r.cache_hit)
        
        avg_response = statistics.mean(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)]
        success_rate = len(successful) / len(results)
        
        return {
            'total_requests': len(results), 
            'successful_requests': len(successful),
            'success_rate': success_rate * 100,
            'avg_response_time': avg_response,
            'p95_response_time': p95_response, 
            'cache_hit_rate': cache_hits / len(successful) * 100,
            'requests_per_second': len(results) / total_time,
            'concurrent_clients': num_clients,
            'targets_met': {
                'sub_200ms_avg': avg_response < 0.2,
                'p95_sub_200ms': p95_response < 0.2,
                'success_rate_95': success_rate >= 0.95
            }
        }


    def run_stress_test(self) -> Dict[str, Any]:
        """Run stress test to find breaking points"""
        print("Running stress test to identify breaking points...")
        
        stress_results = []
        max_clients = 200  # Start high to find limits
        step = 25
        
        for clients in range(25, max_clients + 1, step):
            print(f"Testing {clients} concurrent clients...")
            results = self.run_load_test(clients, 1)
            
            stress_results.append({
                'clients': clients,
                'success_rate': results['success_rate'],
                'avg_response_time': results['avg_response_time'],
                'p95_response_time': results['p95_response_time']
            })
            
            # Stop if success rate drops below 90% or response time > 1s
            if results['success_rate'] < 90 or results['avg_response_time'] > 1.0:
                print(f"Breaking point found at {clients} clients")
                break
                
            time.sleep(2)  # Brief pause between stress tests
        
        return {
            'stress_test_results': stress_results,
            'breaking_point': clients if stress_results else None
        }

    def run_extended_test(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Run extended duration test for stability validation"""
        print(f"Running extended test for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        extended_results = []
        iteration = 0
        
        while time.time() < end_time:
            iteration += 1
            print(f"Extended test iteration {iteration}")
            results = self.run_load_test(10, 2)  # Moderate load
            
            extended_results.append({
                'iteration': iteration,
                'timestamp': time.time(),
                'success_rate': results['success_rate'],
                'avg_response_time': results['avg_response_time']
            })
            
            time.sleep(30)  # 30 second intervals
        
        # Analyze for degradation
        if len(extended_results) >= 2:
            first_half = extended_results[:len(extended_results)//2]
            second_half = extended_results[len(extended_results)//2:]
            
            first_avg_time = statistics.mean([r['avg_response_time'] for r in first_half])
            second_avg_time = statistics.mean([r['avg_response_time'] for r in second_half])
            
            degradation = (second_avg_time - first_avg_time) / first_avg_time * 100
        else:
            degradation = 0
        
        return {
            'duration_minutes': duration_minutes,
            'total_iterations': len(extended_results),
            'performance_degradation_percent': degradation,
            'stability_maintained': abs(degradation) < 10  # Less than 10% degradation
        }


def main():
    """Run comprehensive load testing scenarios"""
    tester = LoadTester()
    
    # Standard load test scenarios
    scenarios = [(10, 3), (25, 2), (50, 1)]
    
    print("=== WebSocket Load Test Results ===\n")
    
    for clients, requests in scenarios:
        results = tester.run_load_test(clients, requests)
        
        print(f"Scenario: {clients} clients × {requests} requests")
        print(f"  Success Rate: {results['success_rate']:.1f}%")
        print(f"  Avg Response: {results['avg_response_time']:.3f}s")
        print(f"  P95 Response: {results['p95_response_time']:.3f}s") 
        print(f"  Cache Hit Rate: {results['cache_hit_rate']:.1f}%")
        
        targets = results['targets_met']
        print(f"  Targets: Avg<200ms {'✓' if targets['sub_200ms_avg'] else '✗'}, "
              f"P95<200ms {'✓' if targets['p95_sub_200ms'] else '✗'}, "
              f"Success≥95% {'✓' if targets['success_rate_95'] else '✗'}")
        print()
    
    # Stress testing
    print("=== Stress Test Results ===")
    stress_results = tester.run_stress_test()
    if stress_results['breaking_point']:
        print(f"Breaking point identified at {stress_results['breaking_point']} concurrent clients")
    print()
    
    # Extended testing (shortened for demo - normally would be 60+ minutes)
    print("=== Extended Stability Test ===")
    extended_results = tester.run_extended_test(duration_minutes=1)  # 1 minute for demo
    print(f"Performance degradation: {extended_results['performance_degradation_percent']:.1f}%")
    print(f"Stability maintained: {'✓' if extended_results['stability_maintained'] else '✗'}")
    print()


if __name__ == '__main__':
    main()