"""
Ollama client integration for local LLM inference.
Provides interface to Ollama API for hypothesis analysis.
"""
import json
import requests
import time
import logging
from typing import Dict, Any, Optional
from threading import Lock

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API with robust connection management and performance optimization."""
    
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip('/')
        self.model_name = "llama3.2:1b"  # Default model optimized for speed
        self._health_lock = Lock()
        self._last_health_check = 0
        self._health_cache_duration = 30  # Cache health status for 30 seconds
        self._is_healthy = False
        self._connection_timeout = 5
        self._request_timeout = 15  # Reduced from 30s for faster timeouts
        self._retry_attempts = 2  # Reduced from 3 for faster failures
        self._retry_delay = 0.5  # Reduced from 1s for faster retries
        
        # Performance optimization parameters
        self._performance_params = {
            "temperature": 0.1,  # Lower temperature for faster inference
            "top_p": 0.9,        # Focused sampling for speed
            "top_k": 40,         # Limited vocabulary for speed
            "num_predict": 150,  # Limit response length for speed
            "repeat_penalty": 1.1,
            "num_ctx": 1024      # Reduced context window for memory efficiency
        }
        
        # Performance monitoring
        self._response_times = []
        self._max_response_history = 100
        self._warm_up_done = False
        
    def is_available(self) -> bool:
        """Check if Ollama service is available with caching."""
        current_time = time.time()
        
        with self._health_lock:
            # Return cached result if still valid
            if current_time - self._last_health_check < self._health_cache_duration:
                return self._is_healthy
            
            # Perform fresh health check
            try:
                if OLLAMA_AVAILABLE:
                    # Try native client first
                    try:
                        ollama.list()
                        self._is_healthy = True
                    except Exception as e:
                        logger.debug(f"Native ollama client failed: {e}")
                        self._is_healthy = False
                else:
                    # Fallback to requests
                    response = requests.get(
                        f"{self.host}/api/tags", 
                        timeout=self._connection_timeout
                    )
                    self._is_healthy = response.status_code == 200
                    
            except Exception as e:
                logger.debug(f"Health check failed: {e}")
                self._is_healthy = False
            
            self._last_health_check = current_time
            return self._is_healthy
    
    def list_models(self) -> list:
        """List available models with retry logic."""
        for attempt in range(self._retry_attempts):
            try:
                if OLLAMA_AVAILABLE:
                    try:
                        models = ollama.list()
                        return models.get('models', [])
                    except Exception as e:
                        logger.debug(f"Native client list_models failed: {e}")
                
                # Fallback to requests
                response = requests.get(
                    f"{self.host}/api/tags", 
                    timeout=self._connection_timeout
                )
                if response.status_code == 200:
                    return response.json().get('models', [])
                    
            except Exception as e:
                logger.debug(f"List models attempt {attempt + 1} failed: {e}")
                if attempt < self._retry_attempts - 1:
                    time.sleep(self._retry_delay * (2 ** attempt))  # Exponential backoff
                
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry with improved error handling."""
        try:
            if OLLAMA_AVAILABLE:
                try:
                    ollama.pull(model_name)
                    return True
                except Exception as e:
                    logger.error(f"Native client pull failed: {e}")
            
            # Fallback to requests
            data = {"name": model_name}
            response = requests.post(
                f"{self.host}/api/pull", 
                json=data, 
                timeout=300
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Model pull failed for {model_name}: {e}")
            return False
    
    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """Generate response from model with performance optimization and monitoring."""
        if not self.is_available():
            logger.warning("Ollama service not available for generation")
            return None
            
        model_to_use = model or self.model_name
        
        # Check if model exists, try to use first available model if not
        models = self.list_models()
        if models and not any(m.get('name', '') == model_to_use for m in models):
            model_to_use = models[0].get('name', self.model_name)
        elif not models:
            logger.warning("No models available for generation")
            return None
            
        # Warm up on first request
        if not self._warm_up_done:
            self._warm_up_done = True
            logger.debug("Performing model warm-up")
            
        start_time = time.time()
        
        for attempt in range(self._retry_attempts):
            try:
                if OLLAMA_AVAILABLE:
                    try:
                        response = ollama.generate(
                            model=model_to_use,
                            prompt=prompt,
                            stream=False,
                            options=self._performance_params
                        )
                        result = response.get('response', '')
                        self._record_response_time(time.time() - start_time)
                        return result
                    except Exception as e:
                        logger.debug(f"Native client generate failed: {e}")
                
                # Fallback to requests with performance parameters
                data = {
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False,
                    "options": self._performance_params
                }
                
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=data,
                    timeout=self._request_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    self._record_response_time(time.time() - start_time)
                    return response_text
                else:
                    logger.warning(f"Generation failed with status {response.status_code}")
                    
            except Exception as e:
                logger.debug(f"Generate attempt {attempt + 1} failed: {e}")
                if attempt < self._retry_attempts - 1:
                    time.sleep(self._retry_delay * (2 ** attempt))
                
        return None
    
    def warm_up(self) -> bool:
        """Warm up the connection by making a small test request."""
        try:
            test_response = self.generate("Hello", self.model_name)
            return test_response is not None
        except Exception as e:
            logger.debug(f"Warm-up failed: {e}")
            return False
    
    def _record_response_time(self, response_time: float) -> None:
        """Record response time for performance monitoring."""
        self._response_times.append(response_time)
        if len(self._response_times) > self._max_response_history:
            self._response_times.pop(0)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        if not self._response_times:
            return {
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "requests_count": 0,
                "sub_200ms_percentage": 0
            }
        
        times_ms = [t * 1000 for t in self._response_times]
        sub_200ms_count = sum(1 for t in times_ms if t < 200)
        
        return {
            "avg_response_time_ms": round(sum(times_ms) / len(times_ms), 2),
            "min_response_time_ms": round(min(times_ms), 2),
            "max_response_time_ms": round(max(times_ms), 2),
            "p95_response_time_ms": round(sorted(times_ms)[int(len(times_ms) * 0.95)], 2),
            "requests_count": len(times_ms),
            "sub_200ms_percentage": round((sub_200ms_count / len(times_ms)) * 100, 2),
            "performance_params": self._performance_params
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status information."""
        status = {
            "available": self.is_available(),
            "models": self.list_models(),
            "default_model": self.model_name,
            "host": self.host,
            "cache_valid": time.time() - self._last_health_check < self._health_cache_duration
        }
        return status
    
    def analyze_hypothesis(self, hypothesis_text: str) -> Dict[str, Any]:
        """Analyze hypothesis and return structured feedback with improved error handling."""
        if not hypothesis_text or not hypothesis_text.strip():
            return {"error": "Empty hypothesis provided"}
            
        prompt = self._build_analysis_prompt(hypothesis_text)
        
        start_time = time.time()
        response = self.generate(prompt)
        response_time = time.time() - start_time
        
        if not response:
            logger.warning(f"Analysis failed for hypothesis: {hypothesis_text[:50]}...")
            return {
                "error": "LLM service unavailable",
                "response_time_ms": int(response_time * 1000),
                "fallback_analysis": {
                    "quality_score": 0.5,
                    "completeness": {
                        "has_baseline": False,
                        "has_change": False,
                        "has_metric": False,
                        "has_outcome": False
                    },
                    "clarity_assessment": "Requires manual review",
                    "testability_score": 0.5,
                    "suggestions": ["Ensure measurable metrics", "Define success criteria"],
                    "strengths": ["Manual review needed"]
                }
            }
        
        # Enhanced JSON response processing with validation and sanitization
        try:
            result = json.loads(response)
            result["response_time_ms"] = int(response_time * 1000)
            
            # Validate required fields
            if not self._validate_response_format(result):
                logger.warning(f"Response validation failed for hypothesis: {hypothesis_text[:50]}...")
                return self._create_fallback_response(response, response_time)
            
            # Sanitize and normalize the response
            result = self._sanitize_and_normalize_response(result)
            
            logger.debug(f"Successfully processed hypothesis analysis in {response_time:.3f}s")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}. Response: {response[:100]}...")
            return self._create_fallback_response(response, response_time)
        except Exception as e:
            logger.error(f"Unexpected error in response processing: {e}")
            return self._create_fallback_response(response, response_time)
    
    def _build_analysis_prompt(self, hypothesis_text: str) -> str:
        """Build structured prompt for hypothesis analysis."""
        return f"""You are an AB testing expert. Analyze the following hypothesis and provide structured feedback.

HYPOTHESIS: "{hypothesis_text}"

ANALYSIS CRITERIA:
- Quality Score: 0.0-1.0 (0.0=poor, 1.0=excellent)
- Completeness: presence of baseline, change, metric, expected outcome
- Clarity: clear, specific, measurable language
- Testability: can be implemented as an AB test

RESPONSE FORMAT (JSON only):
{{
  "quality_score": 0.8,
  "completeness": {{
    "has_baseline": true,
    "has_change": true, 
    "has_metric": true,
    "has_outcome": true
  }},
  "clarity_assessment": "Clear and specific",
  "testability_score": 0.9,
  "suggestions": ["Specific actionable improvement 1", "Specific actionable improvement 2"],
  "strengths": ["What works well in this hypothesis"]
}}

EXAMPLES:
Good hypothesis: "If we change the checkout button from blue to green, then conversion rate will increase by 5% because green creates urgency."
- quality_score: 0.9, all components present, clear metrics

Poor hypothesis: "Making the site better will help users."
- quality_score: 0.2, vague, no measurable outcome, unclear change

Respond with JSON only, no additional text:"""
    
    def _validate_response_format(self, response: Dict[str, Any]) -> bool:
        """Enhanced validation with comprehensive schema checking."""
        required_fields = ["quality_score", "completeness", "clarity_assessment", 
                          "testability_score", "suggestions", "strengths"]
        
        for field in required_fields:
            if field not in response:
                logger.debug(f"Missing required field: {field}")
                return False
        
        # Validate completeness structure
        completeness = response.get("completeness")
        if not isinstance(completeness, dict):
            logger.debug("Completeness is not a dict")
            return False
            
        completeness_fields = ["has_baseline", "has_change", "has_metric", "has_outcome"]
        for field in completeness_fields:
            if field not in completeness:
                logger.debug(f"Missing completeness field: {field}")
                return False
            if not isinstance(completeness[field], bool):
                logger.debug(f"Completeness field {field} is not boolean")
                return False
        
        # Enhanced score validation
        quality_score = response.get("quality_score")
        testability_score = response.get("testability_score")
        
        if not isinstance(quality_score, (int, float)) or not (0 <= quality_score <= 1):
            logger.debug(f"Invalid quality_score: {quality_score}")
            return False
            
        if not isinstance(testability_score, (int, float)) or not (0 <= testability_score <= 1):
            logger.debug(f"Invalid testability_score: {testability_score}")
            return False
        
        # Validate list fields
        suggestions = response.get("suggestions")
        strengths = response.get("strengths")
        
        if not isinstance(suggestions, list) or not all(isinstance(s, str) for s in suggestions):
            logger.debug("Suggestions is not a list of strings")
            return False
            
        if not isinstance(strengths, list) or not all(isinstance(s, str) for s in strengths):
            logger.debug("Strengths is not a list of strings")
            return False
        
        # Validate clarity assessment
        if not isinstance(response.get("clarity_assessment"), str):
            logger.debug("Clarity assessment is not a string")
            return False
            
        return True
    
    def _create_fallback_response(self, raw_response: str, response_time: float) -> Dict[str, Any]:
        """Enhanced fallback response with partial parsing attempts."""
        fallback = {
            "raw_response": raw_response[:500],  # Limit raw response size
            "quality_score": 0.5,
            "completeness": {
                "has_baseline": False,
                "has_change": False,
                "has_metric": False,
                "has_outcome": False
            },
            "clarity_assessment": "Analysis generated but format invalid",
            "testability_score": 0.5,
            "suggestions": ["Review LLM feedback above", "Reformat hypothesis for clarity"],
            "strengths": ["Manual review of raw response needed"],
            "response_time_ms": int(response_time * 1000),
            "format_error": True
        }
        
        # Attempt partial parsing for better user experience
        try:
            if raw_response:
                # Try to extract partial information from raw response
                if "quality" in raw_response.lower():
                    fallback["suggestions"].append("Quality assessment was attempted")
                if "score" in raw_response.lower():
                    fallback["suggestions"].append("Scoring was attempted")
                if "improve" in raw_response.lower():
                    fallback["suggestions"].append("Improvement suggestions were provided")
        except Exception as e:
            logger.debug(f"Partial parsing failed: {e}")
            
        return fallback
    
    def _sanitize_and_normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and normalize response data for consistency."""
        try:
            # Normalize score values
            if isinstance(response.get("quality_score"), (int, float)):
                response["quality_score"] = round(float(response["quality_score"]), 2)
            if isinstance(response.get("testability_score"), (int, float)):
                response["testability_score"] = round(float(response["testability_score"]), 2)
            
            # Sanitize string fields
            if isinstance(response.get("clarity_assessment"), str):
                response["clarity_assessment"] = response["clarity_assessment"].strip()[:200]
            
            # Sanitize lists and limit length
            if isinstance(response.get("suggestions"), list):
                response["suggestions"] = [s.strip()[:100] for s in response["suggestions"][:5] if s and s.strip()]
            
            if isinstance(response.get("strengths"), list):
                response["strengths"] = [s.strip()[:100] for s in response["strengths"][:5] if s and s.strip()]
            
            return response
            
        except Exception as e:
            logger.error(f"Response sanitization failed: {e}")
            return response