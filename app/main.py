from flask import Blueprint, jsonify, render_template, current_app
import datetime
import asyncio

bp = Blueprint('main', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'hypothesis-feedback-tool',
        'version': '1.0.0'
    })


@bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Production health check with memory monitoring."""
    from app.production_manager import production_manager
    
    try:
        health_status = production_manager.get_health_status()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500


@bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Readiness check for production deployment."""
    from app.production_manager import production_manager
    
    try:
        status = production_manager.get_memory_status()
        ready = status.get('within_limits', True) and status.get('pressure_level') != 'critical'
        
        return jsonify({
            'ready': ready,
            'memory_within_limits': status.get('within_limits', True),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 200 if ready else 503
    except Exception as e:
        return jsonify({
            'ready': False,
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 503


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


@bp.route('/performance', methods=['GET'])
def performance_dashboard():
    """Performance monitoring dashboard."""
    from app.performance_monitor import get_performance_summary
    
    try:
        performance_data = get_performance_summary()
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500


@bp.route('/memory', methods=['GET'])
def memory_status():
    """Memory usage and management status."""
    from app.production_manager import production_manager
    from app.hypothesis_cache import hypothesis_cache
    
    try:
        memory_status = production_manager.get_memory_status()
        cache_stats = hypothesis_cache.get_cache_stats()
        cleanup_result = production_manager.maybe_cleanup()
        
        return jsonify({
            'memory': memory_status,
            'cache': cache_stats,
            'cleanup': cleanup_result,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 500