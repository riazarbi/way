"""WebSocket integration for real-time feedback delivery."""
import uuid
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit, disconnect
from flask import request


# Global connection tracking
active_connections = {}
logger = logging.getLogger(__name__)


def create_socketio(app):
    """Initialize Flask-SocketIO with the Flask app."""
    socketio = SocketIO(app, cors_allowed_origins="*", 
                       logger=True, engineio_logger=True)
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connections."""
        session_id = str(uuid.uuid4())
        client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        
        # Store connection info
        active_connections[request.sid] = {
            'session_id': session_id,
            'client_ip': client_ip,
            'connected_at': datetime.utcnow(),
            'last_heartbeat': datetime.utcnow()
        }
        
        logger.info(f"Client connected: {request.sid} (session: {session_id}, IP: {client_ip})")
        
        # Send connection confirmation with session ID
        emit('connected', {
            'session_id': session_id,
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnections."""
        if request.sid in active_connections:
            session_info = active_connections[request.sid]
            logger.info(f"Client disconnected: {request.sid} (session: {session_info['session_id']})")
            del active_connections[request.sid]
        else:
            logger.warning(f"Disconnect received for unknown session: {request.sid}")
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Handle heartbeat messages to maintain connection health."""
        if request.sid in active_connections:
            active_connections[request.sid]['last_heartbeat'] = datetime.utcnow()
            emit('heartbeat_ack', {'timestamp': datetime.utcnow().isoformat()})
        else:
            logger.warning(f"Heartbeat from unknown session: {request.sid}")
            disconnect()
    
    @socketio.on('echo')
    def handle_echo(data):
        """Echo message for testing WebSocket connectivity."""
        if request.sid in active_connections:
            session_info = active_connections[request.sid]
            logger.info(f"Echo request from session {session_info['session_id']}: {data}")
            emit('echo_response', {
                'original_message': data,
                'session_id': session_info['session_id'],
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.warning(f"Echo from unknown session: {request.sid}")
            disconnect()
    
    return socketio


def get_active_connections():
    """Get current active connections count and details."""
    return {
        'count': len(active_connections),
        'connections': {
            sid: {
                'session_id': info['session_id'],
                'client_ip': info['client_ip'],
                'connected_at': info['connected_at'].isoformat(),
                'last_heartbeat': info['last_heartbeat'].isoformat()
            }
            for sid, info in active_connections.items()
        }
    }