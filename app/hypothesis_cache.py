"""
Hypothesis caching system with TF-IDF based similarity matching.
Provides intelligent caching to reduce LLM processing overhead for similar hypotheses.
"""
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class HypothesisCache:
    """Similarity-based cache for hypothesis analysis results."""
    
    def __init__(self, max_size: int = 1000, ttl_hours: float = 24, similarity_threshold: float = 0.75):
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.similarity_threshold = similarity_threshold
        
        # Cache storage: hypothesis_id -> cache_entry
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Text processing for similarity
        self._vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='ascii'
        )
        
        # Similarity index: stores processed texts and vectors
        self._texts: List[str] = []
        self._text_ids: List[str] = []
        self._vectors = None
        
        # Performance metrics
        self._hits = 0
        self._misses = 0
        self._total_lookups = 0
        
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key from hypothesis text."""
        normalized_text = text.strip().lower()
        return hashlib.md5(normalized_text.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() - cache_entry.get('timestamp', 0) > self.ttl_seconds
    
    def _clean_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry.get('timestamp', 0) > self.ttl_seconds
        ]
        
        for key in expired_keys:
            self._remove_entry(key)
            
        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")
    
    def _remove_entry(self, cache_key: str) -> None:
        """Remove entry from cache and similarity index."""
        if cache_key in self._cache:
            # Remove from cache
            del self._cache[cache_key]
            
            # Remove from similarity index
            if cache_key in self._text_ids:
                index = self._text_ids.index(cache_key)
                self._text_ids.pop(index)
                self._texts.pop(index)
                
                # Rebuild vectors if we have entries left
                if self._texts:
                    self._rebuild_vectors()
                else:
                    self._vectors = None
    
    def _rebuild_vectors(self) -> None:
        """Rebuild TF-IDF vectors after removing entries."""
        if len(self._texts) > 0:
            try:
                self._vectors = self._vectorizer.fit_transform(self._texts)
            except Exception as e:
                logger.warning(f"Failed to rebuild vectors: {e}")
                self._vectors = None
    
    def _find_similar_entry(self, text: str) -> Optional[str]:
        """Find most similar cached hypothesis using TF-IDF cosine similarity."""
        if not self._texts or self._vectors is None:
            return None
            
        try:
            # Transform new text using existing vectorizer
            query_vector = self._vectorizer.transform([text])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self._vectors)[0]
            
            # Find best match above threshold
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]
            
            if max_similarity >= self.similarity_threshold:
                similar_id = self._text_ids[max_similarity_idx]
                logger.debug(f"Found similar hypothesis (similarity: {max_similarity:.3f})")
                return similar_id
                
        except Exception as e:
            logger.warning(f"Similarity search failed: {e}")
            
        return None
    
    def get(self, hypothesis_text: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result for hypothesis."""
        self._total_lookups += 1
        
        # Clean expired entries periodically
        if self._total_lookups % 100 == 0:
            self._clean_expired_entries()
        
        # Try exact match first
        cache_key = self._generate_cache_key(hypothesis_text)
        if cache_key in self._cache and not self._is_expired(self._cache[cache_key]):
            self._hits += 1
            entry = self._cache[cache_key]
            entry['cache_hit_type'] = 'exact'
            logger.debug("Cache hit (exact match)")
            return entry['result']
        
        # Try similarity match
        similar_key = self._find_similar_entry(hypothesis_text)
        if similar_key and similar_key in self._cache and not self._is_expired(self._cache[similar_key]):
            self._hits += 1
            entry = self._cache[similar_key]
            entry['cache_hit_type'] = 'similar'
            result = entry['result'].copy()
            result['cache_hit_type'] = 'similar'
            logger.debug("Cache hit (similarity match)")
            return result
        
        self._misses += 1
        return None
    
    def put(self, hypothesis_text: str, analysis_result: Dict[str, Any]) -> None:
        """Store analysis result in cache."""
        cache_key = self._generate_cache_key(hypothesis_text)
        
        # Evict oldest entries if at capacity
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        # Store in cache
        cache_entry = {
            'result': analysis_result.copy(),
            'timestamp': time.time(),
            'text': hypothesis_text,
            'access_count': 1
        }
        self._cache[cache_key] = cache_entry
        
        # Add to similarity index
        self._texts.append(hypothesis_text)
        self._text_ids.append(cache_key)
        
        # Update vectors
        try:
            if len(self._texts) == 1:
                # First entry
                self._vectors = self._vectorizer.fit_transform(self._texts)
            else:
                # Rebuild vectors with new text
                self._vectors = self._vectorizer.fit_transform(self._texts)
        except Exception as e:
            logger.warning(f"Failed to update vectors: {e}")
            # Remove from similarity index if vectorization fails
            self._texts.pop()
            self._text_ids.pop()
        
        logger.debug(f"Cached hypothesis analysis (cache size: {len(self._cache)})")
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry based on timestamp."""
        if not self._cache:
            return
            
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['timestamp'])
        self._remove_entry(oldest_key)
        logger.debug("Evicted oldest cache entry")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        hit_rate = (self._hits / self._total_lookups * 100) if self._total_lookups > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'total_lookups': self._total_lookups,
            'hit_rate_percent': round(hit_rate, 2),
            'similarity_threshold': self.similarity_threshold,
            'ttl_hours': self.ttl_seconds / 3600,
            'memory_usage_entries': len(self._texts)
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._texts.clear()
        self._text_ids.clear()
        self._vectors = None
        logger.info("Cache cleared")
    
    def configure(self, max_size: int = None, ttl_hours: float = None, 
                  similarity_threshold: float = None) -> None:
        """Update cache configuration."""
        if max_size is not None:
            self.max_size = max_size
        if ttl_hours is not None:
            self.ttl_seconds = ttl_hours * 3600
        if similarity_threshold is not None:
            self.similarity_threshold = similarity_threshold
            
        # Clean up if size limit reduced
        while len(self._cache) > self.max_size:
            self._evict_oldest()
            
        logger.info(f"Cache reconfigured: max_size={self.max_size}, "
                   f"ttl_hours={self.ttl_seconds/3600}, "
                   f"similarity_threshold={self.similarity_threshold}")