"""Unit tests for load testing framework"""

import pytest
from load_test import LoadTester, TestResult


def test_test_result():
    result = TestResult(0.15, True, cache_hit=True)
    assert result.response_time == 0.15
    assert result.success is True


def test_load_tester_init():
    tester = LoadTester("http://test:5000")
    assert tester.base_url == "http://test:5000"
    assert len(tester.hypotheses) == 5


def test_analyze_results_success():
    tester = LoadTester()
    results = [TestResult(0.1, True, cache_hit=True), TestResult(0.15, True)]
    
    analysis = tester._analyze_results(results, 1.0, 2)
    
    assert analysis['total_requests'] == 2
    assert analysis['success_rate'] == 100.0
    assert analysis['targets_met']['sub_200ms_avg'] is True


def test_analyze_results_failed():
    tester = LoadTester()
    results = [TestResult(1.0, False, error="Failed")]
    
    analysis = tester._analyze_results(results, 1.0, 1)
    
    assert analysis['success_rate'] == 0
    assert 'error' in analysis


def test_stress_test_structure():
    """Test stress test returns expected structure"""
    tester = LoadTester()
    # Mock the run_load_test to avoid actual network calls
    original_method = tester.run_load_test
    tester.run_load_test = lambda clients, requests: {
        'success_rate': 95.0 if clients < 100 else 80.0,
        'avg_response_time': 0.15 if clients < 100 else 1.2,
        'p95_response_time': 0.18 if clients < 100 else 1.5  
    }
    
    result = tester.run_stress_test()
    
    assert 'stress_test_results' in result
    assert 'breaking_point' in result
    assert isinstance(result['stress_test_results'], list)
    
    tester.run_load_test = original_method


def test_extended_test_structure():
    """Test extended test returns expected structure"""
    tester = LoadTester()
    # Mock the run_load_test to avoid actual network calls
    original_method = tester.run_load_test
    tester.run_load_test = lambda clients, requests: {
        'success_rate': 95.0,
        'avg_response_time': 0.15
    }
    
    result = tester.run_extended_test(duration_minutes=0.1)  # Very short test
    
    assert 'duration_minutes' in result
    assert 'total_iterations' in result  
    assert 'performance_degradation_percent' in result
    assert 'stability_maintained' in result
    
    tester.run_load_test = original_method


if __name__ == '__main__':
    pytest.main([__file__])