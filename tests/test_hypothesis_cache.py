"""
Tests for hypothesis caching system functionality.
"""
import pytest
import time
from app.hypothesis_cache import HypothesisCache


def test_cache_basic_functionality():
    """Test basic cache store and retrieve operations."""
    cache = HypothesisCache(max_size=10, ttl_hours=1)
    
    # Test storage and retrieval
    hypothesis = "If we change button color to green, conversion will increase by 5%"
    analysis = {"quality_score": 0.8, "suggestions": ["test suggestion"]}
    
    # Should miss initially
    assert cache.get(hypothesis) is None
    
    # Store and retrieve
    cache.put(hypothesis, analysis)
    result = cache.get(hypothesis)
    
    assert result is not None
    assert result["quality_score"] == 0.8


def test_cache_similarity_matching():
    """Test similarity-based cache matching."""
    cache = HypothesisCache(max_size=10, ttl_hours=1, similarity_threshold=0.7)
    
    # Store original hypothesis
    original = "If we change the checkout button from blue to green, conversion rate will increase by 5%"
    analysis = {"quality_score": 0.9, "testability_score": 0.8}
    cache.put(original, analysis)
    
    # Test similar hypothesis
    similar = "If we change checkout button to green color, conversion rate will increase by 5%"
    result = cache.get(similar)
    
    # Should find similar match
    assert result is not None
    assert result["quality_score"] == 0.9
    assert result.get("cache_hit_type") == "similar"


def test_cache_expiry():
    """Test cache TTL expiration."""
    cache = HypothesisCache(max_size=10, ttl_hours=0.001)  # Very short TTL (3.6 seconds)
    
    hypothesis = "Test hypothesis for expiry"
    analysis = {"quality_score": 0.5}
    
    cache.put(hypothesis, analysis)
    assert cache.get(hypothesis) is not None
    
    # Wait for expiry (0.001 hours = 3.6 seconds)
    time.sleep(4)
    assert cache.get(hypothesis) is None


def test_cache_size_limit():
    """Test cache size limit and eviction."""
    cache = HypothesisCache(max_size=2, ttl_hours=1)
    
    # Fill cache to capacity
    cache.put("hypothesis1", {"score": 1})
    cache.put("hypothesis2", {"score": 2})
    
    assert len(cache._cache) == 2
    
    # Add third item, should evict oldest
    cache.put("hypothesis3", {"score": 3})
    
    assert len(cache._cache) == 2
    assert cache.get("hypothesis1") is None  # Should be evicted
    assert cache.get("hypothesis3") is not None


def test_cache_stats():
    """Test cache statistics tracking."""
    cache = HypothesisCache(max_size=10, ttl_hours=1)
    
    # Initial stats
    stats = cache.get_stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["hit_rate_percent"] == 0
    
    # Add some cache activity
    hypothesis = "Test hypothesis"
    analysis = {"quality_score": 0.7}
    
    # Miss
    cache.get(hypothesis)
    
    # Store and hit
    cache.put(hypothesis, analysis)
    cache.get(hypothesis)
    
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate_percent"] == 50.0