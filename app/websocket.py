"""WebSocket integration for real-time feedback delivery."""
import uuid
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit, disconnect
from flask import request
from app.connection_manager import connection_manager

logger = logging.getLogger(__name__)


def create_socketio(app):
    """Initialize Flask-SocketIO with the Flask app."""
    socketio = SocketIO(app, cors_allowed_origins="*", 
                       logger=True, engineio_logger=True)
    
    # Start connection manager heartbeat monitoring
    connection_manager.start_heartbeat_monitor()
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connections."""
        session_id = str(uuid.uuid4())
        client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        
        # Add connection to manager
        client_info = {
            'session_id': session_id,
            'client_ip': client_ip,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        if connection_manager.add_connection(request.sid, client_info=client_info):
            logger.info(f"Client connected: {request.sid} (session: {session_id}, IP: {client_ip})")
            
            # Send connection confirmation with session ID
            emit('connected', {
                'session_id': session_id,
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.warning(f"Connection rejected (pool full): {request.sid}")
            emit('error', {
                'message': 'Connection pool full, please try again later',
                'code': 'POOL_FULL'
            })
            disconnect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnections."""
        connection_manager.remove_connection(request.sid)
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping messages for connection health monitoring."""
        connection_manager.update_ping(request.sid)
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})
    
    @socketio.on('pong')
    def handle_pong():
        """Handle pong responses for connection health monitoring."""
        connection_manager.update_pong(request.sid)
    
    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Handle heartbeat messages to maintain connection health."""
        connection = connection_manager.get_connection(request.sid)
        if connection:
            connection_manager.update_pong(request.sid)
            emit('heartbeat_ack', {'timestamp': datetime.utcnow().isoformat()})
        else:
            logger.warning(f"Heartbeat from unknown session: {request.sid}")
            disconnect()
    
    @socketio.on('echo')
    def handle_echo(data):
        """Echo message for testing WebSocket connectivity."""
        connection = connection_manager.get_connection(request.sid)
        if connection:
            logger.info(f"Echo request from session {connection.client_info.get('session_id')}: {data}")
            emit('echo_response', {
                'original_message': data,
                'session_id': connection.client_info.get('session_id'),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.warning(f"Echo from unknown session: {request.sid}")
            disconnect()
    
    return socketio


def get_active_connections():
    """Get current active connections count and details."""
    return connection_manager.get_active_connections()