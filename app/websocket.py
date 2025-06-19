"""WebSocket integration for real-time feedback delivery."""
import uuid
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit, disconnect
from flask import request
from app.connection_manager import connection_manager
from app.session_manager import session_manager
from app.message_queue import message_queue

logger = logging.getLogger(__name__)


def create_socketio(app):
    """Initialize Flask-SocketIO with the Flask app."""
    socketio = SocketIO(app, cors_allowed_origins="*", 
                       logger=True, engineio_logger=True)
    
    # Start connection manager heartbeat monitoring
    connection_manager.start_heartbeat_monitor()
    
    # Start session manager cleanup monitoring
    session_manager.start_cleanup_monitor()
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connections."""
        client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        
        # Check for existing session ID from query parameters
        session_id = request.args.get('session_id')
        
        if session_id:
            # Validate existing session
            session = session_manager.get_session(session_id)
            if not session:
                logger.warning(f"Invalid session ID provided: {session_id}")
                emit('error', {
                    'message': 'Invalid or expired session ID',
                    'code': 'INVALID_SESSION'
                })
                disconnect()
                return
        else:
            # Create new session
            session_id = session_manager.create_session()
        
        # Add connection to manager
        client_info = {
            'session_id': session_id,
            'client_ip': client_ip,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        if connection_manager.add_connection(request.sid, client_info=client_info):
            # Link WebSocket to session
            if session_manager.link_websocket(session_id, request.sid):
                logger.info(f"Client connected: {request.sid} (session: {session_id}, IP: {client_ip})")
                
                # Send connection confirmation with session ID
                emit('connected', {
                    'session_id': session_id,
                    'status': 'connected',
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                logger.error(f"Failed to link WebSocket to session: {session_id}")
                connection_manager.remove_connection(request.sid)
                emit('error', {
                    'message': 'Session linking failed',
                    'code': 'LINK_FAILED'
                })
                disconnect()
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
        # Unlink WebSocket from session
        session_id = session_manager.unlink_websocket(request.sid)
        if session_id:
            logger.info(f"WebSocket {request.sid} disconnected from session {session_id}")
        
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
    
    @socketio.on('message_delivered')
    def handle_message_delivered(data):
        """Handle message delivery confirmation from client."""
        message_id = data.get('message_id')
        if message_id:
            success = message_queue.confirm_delivery(message_id)
            if success:
                logger.debug(f"Message delivery confirmed: {message_id}")
            else:
                logger.warning(f"Failed to confirm delivery: {message_id}")
        else:
            logger.warning("Message delivery confirmation without message_id")
    
    return socketio


def get_active_connections():
    """Get current active connections count and details."""
    return connection_manager.get_active_connections()