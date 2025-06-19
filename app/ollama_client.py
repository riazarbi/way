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
    """Client for interacting with Ollama API with robust connection management."""
    
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip('/')
        self.model_name = "llama3.2:1b"  # Default model
        self._health_lock = Lock()
        self._last_health_check = 0
        self._health_cache_duration = 30  # Cache health status for 30 seconds
        self._is_healthy = False
        self._connection_timeout = 5
        self._request_timeout = 30
        self._retry_attempts = 3
        self._retry_delay = 1
        
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
        """Generate response from model with robust error handling and retries."""
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
            
        for attempt in range(self._retry_attempts):
            try:
                if OLLAMA_AVAILABLE:
                    try:
                        response = ollama.generate(
                            model=model_to_use,
                            prompt=prompt,
                            stream=False
                        )
                        return response.get('response', '')
                    except Exception as e:
                        logger.debug(f"Native client generate failed: {e}")
                
                # Fallback to requests
                data = {
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=data,
                    timeout=self._request_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '')
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
        
        # Try to parse JSON response, fallback to basic structure
        try:
            result = json.loads(response)
            result["response_time_ms"] = int(response_time * 1000)
            # Validate required fields
            if not self._validate_response_format(result):
                return self._create_fallback_response(response, response_time)
            return result
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse JSON response: {response[:100]}...")
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
        """Validate that response contains required fields."""
        required_fields = ["quality_score", "completeness", "clarity_assessment", 
                          "testability_score", "suggestions", "strengths"]
        
        for field in required_fields:
            if field not in response:
                return False
        
        # Validate completeness structure
        if not isinstance(response.get("completeness"), dict):
            return False
            
        completeness_fields = ["has_baseline", "has_change", "has_metric", "has_outcome"]
        for field in completeness_fields:
            if field not in response["completeness"]:
                return False
        
        # Validate score ranges
        quality_score = response.get("quality_score", 0)
        testability_score = response.get("testability_score", 0)
        
        if not (0 <= quality_score <= 1) or not (0 <= testability_score <= 1):
            return False
            
        return True
    
    def _create_fallback_response(self, raw_response: str, response_time: float) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        return {
            "raw_response": raw_response,
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