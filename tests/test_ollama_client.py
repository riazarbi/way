"""
Unit tests for Ollama client integration.
"""
import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from app.ollama_client import OllamaClient, OLLAMA_AVAILABLE


class TestOllamaClient:
    """Test suite for OllamaClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
        # Reset health cache for each test
        self.client._last_health_check = 0
        self.client._is_healthy = False
    
    def test_init(self):
        """Test client initialization."""
        client = OllamaClient("http://localhost:11434")
        assert client.host == "http://localhost:11434"
        assert client.model_name == "llama3.2:1b"
        assert client._retry_attempts == 3
        assert client._connection_timeout == 5
    
    def test_init_host_cleanup(self):
        """Test host URL cleanup during initialization."""
        client = OllamaClient("http://localhost:11434/")
        assert client.host == "http://localhost:11434"
    
    @patch('requests.get')
    def test_is_available_success(self, mock_get):
        """Test successful availability check."""
        mock_get.return_value.status_code = 200
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            result = self.client.is_available()
            assert result is True
            assert self.client._is_healthy is True
    
    @patch('requests.get')
    def test_is_available_failure(self, mock_get):
        """Test failed availability check."""
        mock_get.side_effect = Exception("Connection failed")
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            result = self.client.is_available()
            assert result is False
            assert self.client._is_healthy is False
    
    def test_is_available_caching(self):
        """Test health check caching."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            
            # First call should make request
            self.client.is_available()
            assert mock_get.call_count == 1
            
            # Second call within cache duration should not make request
            self.client.is_available()
            assert mock_get.call_count == 1
            
            # After cache expiry, should make new request
            self.client._last_health_check = time.time() - 40
            self.client.is_available()
            assert mock_get.call_count == 2
    
    @patch('requests.get')
    def test_list_models_success(self, mock_get):
        """Test successful model listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [{'name': 'llama3.2:1b'}, {'name': 'llama3.2:3b'}]
        }
        mock_get.return_value = mock_response
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            models = self.client.list_models()
            assert len(models) == 2
            assert models[0]['name'] == 'llama3.2:1b'
    
    @patch('requests.get')
    def test_list_models_with_retry(self, mock_get):
        """Test model listing with retry on failure."""
        # First call fails, second succeeds
        mock_get.side_effect = [
            Exception("Connection failed"),
            Mock(status_code=200, json=lambda: {'models': [{'name': 'test'}]})
        ]
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            models = self.client.list_models()
            assert len(models) == 1
            assert mock_get.call_count == 2
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """Test successful text generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': 'Generated text'}
        mock_post.return_value = mock_response
        
        with patch.object(self.client, 'is_available', return_value=True), \
             patch.object(self.client, 'list_models', return_value=[{'name': 'llama3.2:1b'}]), \
             patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            
            result = self.client.generate("Test prompt")
            assert result == "Generated text"
    
    def test_generate_service_unavailable(self):
        """Test generation when service is unavailable."""
        with patch.object(self.client, 'is_available', return_value=False):
            result = self.client.generate("Test prompt")
            assert result is None
    
    def test_generate_no_models(self):
        """Test generation when no models available."""
        with patch.object(self.client, 'is_available', return_value=True), \
             patch.object(self.client, 'list_models', return_value=[]):
            
            result = self.client.generate("Test prompt")
            assert result is None
    
    def test_warm_up_success(self):
        """Test successful connection warm-up."""
        with patch.object(self.client, 'generate', return_value="Hello response"):
            result = self.client.warm_up()
            assert result is True
    
    def test_warm_up_failure(self):
        """Test failed connection warm-up."""
        with patch.object(self.client, 'generate', return_value=None):
            result = self.client.warm_up()
            assert result is False
    
    def test_get_health_status(self):
        """Test health status reporting."""
        with patch.object(self.client, 'is_available', return_value=True), \
             patch.object(self.client, 'list_models', return_value=[{'name': 'test'}]):
            
            status = self.client.get_health_status()
            assert status['available'] is True
            assert len(status['models']) == 1
            assert status['default_model'] == 'llama3.2:1b'
            assert status['host'] == 'http://127.0.0.1:11434'
    
    def test_analyze_hypothesis_empty_input(self):
        """Test hypothesis analysis with empty input."""
        result = self.client.analyze_hypothesis("")
        assert "error" in result
        assert result["error"] == "Empty hypothesis provided"
        
        result = self.client.analyze_hypothesis("   ")
        assert "error" in result
    
    def test_analyze_hypothesis_success(self):
        """Test successful hypothesis analysis."""
        mock_response = json.dumps({
            "clarity_score": 4,
            "testability": "Good",
            "suggestions": ["Add metrics", "Define timeline"]
        })
        
        with patch.object(self.client, 'generate', return_value=mock_response):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert result["clarity_score"] == 4
            assert result["testability"] == "Good"
            assert "response_time_ms" in result
            assert isinstance(result["response_time_ms"], int)
    
    def test_analyze_hypothesis_service_unavailable(self):
        """Test hypothesis analysis when service unavailable."""
        with patch.object(self.client, 'generate', return_value=None):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert "error" in result
            assert "fallback_analysis" in result
            assert result["fallback_analysis"]["clarity_score"] == 3
    
    def test_analyze_hypothesis_invalid_json(self):
        """Test hypothesis analysis with invalid JSON response."""
        with patch.object(self.client, 'generate', return_value="Invalid JSON response"):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert "raw_response" in result
            assert result["raw_response"] == "Invalid JSON response"
            assert result["clarity_score"] == 3
    
    @patch('requests.post')
    def test_pull_model_success(self, mock_post):
        """Test successful model pulling."""
        mock_post.return_value.status_code = 200
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            result = self.client.pull_model("test-model")
            assert result is True
    
    @patch('requests.post')
    def test_pull_model_failure(self, mock_post):
        """Test failed model pulling."""
        mock_post.side_effect = Exception("Pull failed")
        
        with patch('app.ollama_client.OLLAMA_AVAILABLE', False):
            result = self.client.pull_model("test-model")
            assert result is False


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama package not available")
class TestOllamaNativeClient:
    """Test suite for native Ollama client integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
        self.client._last_health_check = 0
        self.client._is_healthy = False
    
    @patch('ollama.list')
    def test_is_available_native_success(self, mock_list):
        """Test availability check with native client."""
        mock_list.return_value = {'models': []}
        
        result = self.client.is_available()
        assert result is True
        mock_list.assert_called_once()
    
    @patch('ollama.generate')
    def test_generate_native_success(self, mock_generate):
        """Test generation with native client."""
        mock_generate.return_value = {'response': 'Native response'}
        
        with patch.object(self.client, 'is_available', return_value=True), \
             patch.object(self.client, 'list_models', return_value=[{'name': 'llama3.2:1b'}]):
            
            result = self.client.generate("Test prompt")
            assert result == "Native response"
            mock_generate.assert_called_once()