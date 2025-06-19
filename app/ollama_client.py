"""
Ollama client integration for local LLM inference.
Provides interface to Ollama API for hypothesis analysis.
"""
import json
import requests
import time
from typing import Dict, Any, Optional


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip('/')
        self.model_name = "llama3.2:1b"  # Default model
        
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
        except:
            pass
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            data = {"name": model_name}
            response = requests.post(
                f"{self.host}/api/pull", 
                json=data, 
                timeout=300
            )
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """Generate response from model."""
        if not self.is_available():
            return None
            
        model_to_use = model or self.model_name
        
        # Check if model exists, try to use first available model if not
        models = self.list_models()
        if models and not any(m['name'] == model_to_use for m in models):
            model_to_use = models[0]['name']
        elif not models:
            return None
            
        try:
            data = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
        except:
            pass
        return None
    
    def analyze_hypothesis(self, hypothesis_text: str) -> Dict[str, Any]:
        """Analyze hypothesis and return structured feedback."""
        if not hypothesis_text or not hypothesis_text.strip():
            return {"error": "Empty hypothesis provided"}
            
        prompt = f"""Analyze this AB test hypothesis and provide brief feedback:
        
Hypothesis: "{hypothesis_text}"

Provide a JSON response with:
- clarity_score: 1-5 rating
- testability: brief assessment
- suggestions: 1-2 key improvements

Keep response under 100 words total."""
        
        response = self.generate(prompt)
        
        if not response:
            return {
                "error": "LLM service unavailable",
                "fallback_analysis": {
                    "clarity_score": 3,
                    "testability": "Requires manual review",
                    "suggestions": ["Ensure measurable metrics", "Define success criteria"]
                }
            }
        
        # Try to parse JSON response, fallback to basic structure
        try:
            return json.loads(response)
        except:
            return {
                "raw_response": response,
                "clarity_score": 3,
                "testability": "Analysis generated",
                "suggestions": ["Review LLM feedback above"]
            }