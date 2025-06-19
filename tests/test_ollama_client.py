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
        assert client._retry_attempts == 2  # Optimized from 3 to 2
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
        """Test successful hypothesis analysis with new format."""
        mock_response = json.dumps({
            "quality_score": 0.8,
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "Clear and specific",
            "testability_score": 0.9,
            "suggestions": ["Add statistical significance testing", "Consider sample size"],
            "strengths": ["Clear hypothesis structure", "Measurable outcome"]
        })
        
        with patch.object(self.client, 'generate', return_value=mock_response):
            result = self.client.analyze_hypothesis("If we change button color from blue to green, conversion rate will increase by 5%")
            
            assert result["quality_score"] == 0.8
            assert result["testability_score"] == 0.9
            assert "completeness" in result
            assert result["completeness"]["has_baseline"] is True
            assert "response_time_ms" in result
            assert isinstance(result["response_time_ms"], int)
    
    def test_analyze_hypothesis_service_unavailable(self):
        """Test hypothesis analysis when service unavailable."""
        with patch.object(self.client, 'generate', return_value=None):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert "error" in result
            assert "fallback_analysis" in result
            assert result["fallback_analysis"]["quality_score"] == 0.5
            assert "completeness" in result["fallback_analysis"]
    
    def test_analyze_hypothesis_invalid_json(self):
        """Test hypothesis analysis with invalid JSON response."""
        with patch.object(self.client, 'generate', return_value="Invalid JSON response"):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert "raw_response" in result
            assert result["raw_response"] == "Invalid JSON response"
            assert result["quality_score"] == 0.5
            assert "format_error" in result
            assert result["format_error"] is True
    
    def test_validate_response_format_valid(self):
        """Test response format validation with valid response."""
        valid_response = {
            "quality_score": 0.8,
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "Clear",
            "testability_score": 0.9,
            "suggestions": ["Test suggestion"],
            "strengths": ["Test strength"]
        }
        
        assert self.client._validate_response_format(valid_response) is True
    
    def test_validate_response_format_invalid_score(self):
        """Test response format validation with invalid score ranges."""
        invalid_response = {
            "quality_score": 1.5,  # Invalid: > 1.0
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "Clear",
            "testability_score": 0.9,
            "suggestions": ["Test suggestion"],
            "strengths": ["Test strength"]
        }
        
        assert self.client._validate_response_format(invalid_response) is False
    
    def test_validate_response_format_missing_fields(self):
        """Test response format validation with missing required fields."""
        invalid_response = {
            "quality_score": 0.8,
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            }
            # Missing other required fields
        }
        
        assert self.client._validate_response_format(invalid_response) is False
    
    def test_build_analysis_prompt(self):
        """Test prompt building for hypothesis analysis."""
        hypothesis = "If we change button color, conversion will increase"
        prompt = self.client._build_analysis_prompt(hypothesis)
        
        assert "AB testing expert" in prompt
        assert hypothesis in prompt
        assert "quality_score" in prompt
        assert "JSON only" in prompt
        assert "0.0-1.0" in prompt
    
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
    
    def test_performance_parameters(self):
        """Test performance optimization parameters."""
        params = self.client._performance_params
        
        # Verify optimization parameters
        assert params["temperature"] == 0.1  # Low for speed
        assert params["top_p"] == 0.9  # Focused sampling
        assert params["top_k"] == 40  # Limited vocabulary
        assert params["num_predict"] == 150  # Limited response
        assert params["num_ctx"] == 1024  # Reduced context
        assert params["repeat_penalty"] == 1.1
    
    def test_performance_metrics_empty(self):
        """Test performance metrics with no data."""
        metrics = self.client.get_performance_metrics()
        
        assert metrics["avg_response_time_ms"] == 0
        assert metrics["requests_count"] == 0
        assert metrics["sub_200ms_percentage"] == 0
    
    def test_performance_metrics_with_data(self):
        """Test performance metrics with recorded data."""
        # Record some response times
        self.client._record_response_time(0.1)  # 100ms
        self.client._record_response_time(0.15)  # 150ms
        self.client._record_response_time(0.25)  # 250ms
        
        metrics = self.client.get_performance_metrics()
        
        assert metrics["requests_count"] == 3
        assert metrics["avg_response_time_ms"] == 166.67
        assert metrics["min_response_time_ms"] == 100
        assert metrics["max_response_time_ms"] == 250
        assert metrics["sub_200ms_percentage"] == 66.67  # 2 out of 3


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


class TestResponseProcessing:
    """Test suite for enhanced response processing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
    
    def test_sanitize_and_normalize_response_valid(self):
        """Test response sanitization with valid data."""
        response = {
            "quality_score": 0.875,
            "testability_score": 0.923,
            "clarity_assessment": "  Clear and well-defined  ",
            "suggestions": ["Suggestion 1", "Suggestion 2", ""],
            "strengths": ["Strength 1", "Strength 2"]
        }
        
        result = self.client._sanitize_and_normalize_response(response)
        
        assert result["quality_score"] == 0.88  # Rounded to 2 decimal places
        assert result["testability_score"] == 0.92
        assert result["clarity_assessment"] == "Clear and well-defined"
        assert len(result["suggestions"]) == 2  # Empty suggestion removed
    
    def test_enhanced_validation_detailed_logging(self):
        """Test enhanced validation with detailed error logging."""
        invalid_response = {
            "quality_score": 0.8,
            "completeness": {
                "has_baseline": "true",  # String instead of boolean
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "Clear",
            "testability_score": 0.9,
            "suggestions": ["Test"],
            "strengths": ["Test"]
        }
        
        result = self.client._validate_response_format(invalid_response)
        assert result is False
    
    def test_enhanced_validation_list_fields(self):
        """Test enhanced validation of list fields."""
        invalid_response = {
            "quality_score": 0.8,
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "Clear",
            "testability_score": 0.9,
            "suggestions": "Not a list",  # Should be list
            "strengths": ["Test"]
        }
        
        result = self.client._validate_response_format(invalid_response)
        assert result is False
    
    def test_create_fallback_response_partial_parsing(self):
        """Test enhanced fallback response with partial parsing."""
        raw_response = "The quality of this hypothesis is good and needs improvement"
        response_time = 0.5
        
        result = self.client._create_fallback_response(raw_response, response_time)
        
        assert result["format_error"] is True
        assert result["response_time_ms"] == 500
        assert "Quality assessment was attempted" in result["suggestions"]
    
    def test_analyze_hypothesis_with_enhanced_processing(self):
        """Test complete hypothesis analysis with enhanced processing."""
        mock_response = json.dumps({
            "quality_score": 0.875,
            "completeness": {
                "has_baseline": True,
                "has_change": True,
                "has_metric": True,
                "has_outcome": True
            },
            "clarity_assessment": "  Clear and specific  ",
            "testability_score": 0.923,
            "suggestions": ["Suggestion 1", "Suggestion 2", ""],
            "strengths": ["Strength 1"]
        })
        
        with patch.object(self.client, 'generate', return_value=mock_response):
            result = self.client.analyze_hypothesis("Test hypothesis")
            
            assert result["quality_score"] == 0.88  # Rounded
            assert result["testability_score"] == 0.92  # Rounded
            assert result["clarity_assessment"] == "Clear and specific"  # Trimmed
            assert len(result["suggestions"]) == 2  # Empty removed