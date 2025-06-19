from flask import Blueprint, request, jsonify, current_app
import datetime
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')

# Request/Response logging middleware
@bp.before_request  
def log_request_info():
    """Log incoming API requests."""
    logger.info(f"API Request: {request.method} {request.path} from {request.remote_addr}")
    if request.is_json and request.get_json(silent=True):
        logger.debug(f"Request payload: {request.get_json(silent=True)}")

@bp.after_request
def log_response_info(response):
    """Log API responses."""
    logger.info(f"API Response: {response.status_code} for {request.method} {request.path}")
    return response

def validate_hypothesis_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate hypothesis submission data."""
    errors = {}
    
    # Required fields
    required_fields = ['hypothesis', 'experiment_type', 'metrics']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.setdefault('required_fields', []).append(f"{field} is required")
    
    # Field validation
    if 'hypothesis' in data:
        if not isinstance(data['hypothesis'], str):
            errors.setdefault('type_errors', []).append("hypothesis must be a string")
        elif len(data['hypothesis']) > 1000:
            errors.setdefault('length_errors', []).append("hypothesis must be less than 1000 characters")
        elif len(data['hypothesis']) < 10:
            errors.setdefault('length_errors', []).append("hypothesis must be at least 10 characters")
    
    if 'experiment_type' in data:
        valid_types = ['a_b_test', 'multivariate', 'feature_flag', 'split_test']
        if data['experiment_type'] not in valid_types:
            errors.setdefault('value_errors', []).append(f"experiment_type must be one of: {', '.join(valid_types)}")
    
    if 'metrics' in data:
        if not isinstance(data['metrics'], list):
            errors.setdefault('type_errors', []).append("metrics must be a list")
        elif len(data['metrics']) == 0:
            errors.setdefault('value_errors', []).append("at least one metric is required")
    
    return errors

@bp.route('/hypothesis', methods=['POST'])
def submit_hypothesis():
    """Submit a hypothesis for AI-powered feedback."""
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body cannot be empty',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }), 400
        
        # Validate hypothesis data
        errors = validate_hypothesis_data(data)
        if errors:
            return jsonify({
                'error': 'Validation failed',
                'details': errors,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }), 400
        
        # For now, accept the hypothesis and return success
        # Future integration: trigger LLM analysis via WebSocket
        hypothesis_id = f"hyp_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Hypothesis submitted: {hypothesis_id}")
        
        return jsonify({
            'status': 'submitted',
            'hypothesis_id': hypothesis_id,
            'message': 'Hypothesis received and queued for analysis',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'data': {
                'hypothesis': data['hypothesis'],
                'experiment_type': data['experiment_type'],
                'metrics': data['metrics']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing hypothesis submission: {str(e)}")
        return jsonify({
            'error': 'Internal server error processing hypothesis',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500

@bp.route('/health', methods=['GET'])
def api_health():
    """API-specific health check endpoint."""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'hypothesis-feedback-api',
            'version': '1.0.0',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'endpoints': {
                'hypothesis_submission': '/api/hypothesis',
                'health_check': '/api/health'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500

# Error handlers for the API blueprint
@bp.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors."""
    return jsonify({
        'error': 'Method not allowed',
        'allowed_methods': error.description,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 405

@bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle request entity too large errors."""
    return jsonify({
        'error': 'Request entity too large',
        'max_content_length': current_app.config.get('MAX_CONTENT_LENGTH', 'Not configured'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 413