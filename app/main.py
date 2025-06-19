from flask import Blueprint, jsonify
import datetime

bp = Blueprint('main', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'hypothesis-feedback-tool',
        'version': '1.0.0'
    })