"""HTTP API integration tests."""
import pytest
import json


class TestAPIEndpoints:
    """Test HTTP API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'connections' in data
    
    def test_connections_status(self, client):
        """Test connections status endpoint."""
        response = client.get('/api/connections')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'count' in data
        assert 'max_connections' in data
        assert isinstance(data['connections'], list)
    
    def test_hypothesis_submission(self, client):
        """Test hypothesis submission endpoint."""
        hypothesis_data = {
            'hypothesis': 'Button color change increases CTR',
            'context': 'E-commerce page',
            'metric': 'click-through rate'
        }
        
        response = client.post('/api/hypothesis',
                             data=json.dumps(hypothesis_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'analyzed'
        assert 'request_id' in data
        assert 'analysis' in data
    
    def test_invalid_requests(self, client):
        """Test invalid request handling."""
        # Missing data
        response = client.post('/api/hypothesis', 
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Invalid JSON
        response = client.post('/api/hypothesis',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
        
        # Non-existent endpoint
        response = client.get('/api/nonexistent')
        assert response.status_code == 404