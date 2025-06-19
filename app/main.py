from flask import Blueprint, jsonify, render_template
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


@bp.route('/connections', methods=['GET'])
def connection_status():
    """Get active WebSocket connections status."""
    from app.websocket import get_active_connections
    
    connections_info = get_active_connections()
    
    return jsonify({
        'active_connections': connections_info['count'],
        'connections': connections_info['connections'],
        'timestamp': datetime.datetime.utcnow().isoformat()
    })


@bp.route('/test', methods=['GET'])
def test_websocket():
    """Serve WebSocket test page."""
    return render_template('test_websocket.html')