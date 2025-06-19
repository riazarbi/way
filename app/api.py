from flask import Blueprint, request, jsonify, current_app
import datetime
import logging
from functools import wraps
from .ollama_client import OllamaClient

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Configure logging
logger = logging.getLogger(__name__)

def log_request_response(f):
    """Decorator to log API requests and responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request
        logger.info(f"API Request: {request.method} {request.path} - IP: {request.remote_addr}")
        if request.method == 'POST' and request.is_json:
            logger.info(f"Request data: {request.json}")
        
        # Execute function
        start_time = datetime.datetime.utcnow()
        response = f(*args, **kwargs)
        end_time = datetime.datetime.utcnow()
        
        # Log response
        response_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"API Response: {request.path} - Status: {response[1] if isinstance(response, tuple) else 200} - Time: {response_time:.2f}ms")
        
        return response
    return decorated_function

def validate_hypothesis_data(data):
    """Validate hypothesis submission data."""
    if not data:
        return False, "No data provided"
    
    required_fields = ['hypothesis', 'context', 'metric']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not isinstance(data[field], str) or not data[field].strip():
            return False, f"Field '{field}' must be a non-empty string"
    
    # Validate field lengths
    if len(data['hypothesis']) > 1000:
        return False, "Hypothesis text too long (max 1000 characters)"
    
    if len(data['context']) > 500:
        return False, "Context description too long (max 500 characters)"
    
    if len(data['metric']) > 200:
        return False, "Metric description too long (max 200 characters)"
    
    return True, None

@api_bp.route('/connections', methods=['GET'])
@log_request_response
def connections_status():
    """Get current WebSocket connections status."""
    from flask import current_app
    
    # Get connection details from connection manager
    if hasattr(current_app, 'connection_manager'):
        cm = current_app.connection_manager
        connection_count = cm.get_connection_count()
        max_connections = getattr(cm, 'max_connections', 100)
        connections = []
        
        # Get basic connection info (avoiding sensitive data)
        for conn_id, conn_info in cm.connections.items():
            connections.append({
                'id': conn_id,
                'connected_at': conn_info.get('connected_at', '').isoformat() if conn_info.get('connected_at') else '',
                'last_ping': conn_info.get('last_ping', '').isoformat() if conn_info.get('last_ping') else ''
            })
    else:
        connection_count = 0
        max_connections = 100
        connections = []
    
    return jsonify({
        'count': connection_count,
        'max_connections': max_connections,
        'connections': connections
    }), 200

@api_bp.route('/health', methods=['GET'])  
@log_request_response
def health_check():
    """Health check endpoint for application monitoring."""
    from flask import current_app
    
    # Get connection count from connection manager
    connection_count = 0
    if hasattr(current_app, 'connection_manager'):
        connection_count = current_app.connection_manager.get_connection_count()
    
    # Check Ollama service status
    ollama_client = OllamaClient()
    ollama_status = ollama_client.is_available()
    ollama_models = ollama_client.list_models()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'hypothesis-feedback-tool',
        'version': '1.0.0',
        'uptime': 'active',
        'connections': connection_count,
        'ollama': {
            'available': ollama_status,
            'models': len(ollama_models),
            'model_names': [m.get('name', '') for m in ollama_models]
        }
    }), 200

@api_bp.route('/performance', methods=['GET'])
@log_request_response
def performance_metrics():
    """Performance metrics endpoint."""
    from flask import current_app
    
    # Get performance metrics from ollama client
    ollama_client = OllamaClient()
    performance_metrics = ollama_client.get_performance_metrics()
    
    return jsonify({
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'performance': performance_metrics
    }), 200

@api_bp.route('/hypothesis', methods=['POST'])
@log_request_response
def submit_hypothesis():
    """Submit hypothesis for AI-powered feedback."""
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({
                'error': 'Invalid content type',
                'message': 'Content-Type must be application/json'
            }), 400
        
        # Get and validate request data
        data = request.get_json()
        is_valid, error_message = validate_hypothesis_data(data)
        
        if not is_valid:
            return jsonify({
                'error': 'Validation failed',
                'message': error_message
            }), 400
        
        # Process hypothesis submission
        request_id = f"req_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze hypothesis with LLM
        ollama_client = OllamaClient()
        analysis = ollama_client.analyze_hypothesis(data['hypothesis'])
        
        # Log successful submission
        logger.info(f"Hypothesis submitted successfully: {request_id}")
        
        # Return success response with AI analysis
        return jsonify({
            'message': 'Hypothesis analyzed successfully',
            'request_id': request_id,
            'status': 'analyzed',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'data': {
                'hypothesis': data['hypothesis'],
                'context': data['context'],
                'metric': data['metric']
            },
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing hypothesis submission: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API routes."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for API routes."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@api_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 errors for API routes."""
    return jsonify({
        'error': 'Request too large',
        'message': 'The request payload is too large'
    }), 413