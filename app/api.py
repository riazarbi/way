from flask import Blueprint, request, jsonify, current_app
import datetime
import logging
from functools import wraps

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
    
    required_fields = ['hypothesis', 'control_group', 'test_group', 'success_metric']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not isinstance(data[field], str) or not data[field].strip():
            return False, f"Field '{field}' must be a non-empty string"
    
    # Validate field lengths
    if len(data['hypothesis']) > 1000:
        return False, "Hypothesis text too long (max 1000 characters)"
    
    if len(data['control_group']) > 500:
        return False, "Control group description too long (max 500 characters)"
    
    if len(data['test_group']) > 500:
        return False, "Test group description too long (max 500 characters)"
    
    if len(data['success_metric']) > 200:
        return False, "Success metric description too long (max 200 characters)"
    
    return True, None

@api_bp.route('/health', methods=['GET'])
@log_request_response
def health_check():
    """Health check endpoint for application monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'hypothesis-feedback-tool',
        'version': '1.0.0',
        'uptime': 'active'
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
        hypothesis_id = f"hyp_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Log successful submission
        logger.info(f"Hypothesis submitted successfully: {hypothesis_id}")
        
        # Return success response
        return jsonify({
            'message': 'Hypothesis submitted successfully',
            'hypothesis_id': hypothesis_id,
            'status': 'accepted',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'data': {
                'hypothesis': data['hypothesis'],
                'control_group': data['control_group'],
                'test_group': data['test_group'],
                'success_metric': data['success_metric']
            }
        }), 201
        
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