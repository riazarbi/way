"""Session management for linking HTTP requests to WebSocket connections."""

import uuid
import threading
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions and HTTP-to-WebSocket routing."""
    
    def __init__(self, session_timeout: int = 1800):
        self.session_timeout = session_timeout
        self.sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.websocket_to_session: Dict[str, str] = {}  # websocket_sid -> session_id
        self.lock = threading.RLock()
        
    def start_cleanup_monitor(self):
        """Start cleanup monitor (minimal implementation)."""
        logger.info("Session cleanup monitor started (minimal)")
    
    def stop_cleanup_monitor(self):
        """Stop cleanup monitor."""
        logger.info("Session cleanup monitor stopped")
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        
        with self.lock:
            self.sessions[session_id] = {
                'session_id': session_id,
                'created_at': datetime.utcnow(),
                'websocket_sid': None,
                'last_activity': datetime.utcnow(),
                'is_active': True
            }
            
        logger.info(f"Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID if valid."""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and self._is_session_valid(session):
                return session
            elif session:
                session['is_active'] = False
                logger.info(f"Session expired: {session_id}")
            return None
    
    def link_websocket(self, session_id: str, websocket_sid: str) -> bool:
        """Link a WebSocket connection to a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session or not self._is_session_valid(session):
                return False
            
            # Remove old link if exists
            if session['websocket_sid']:
                old_sid = session['websocket_sid']
                self.websocket_to_session.pop(old_sid, None)
            
            # Create new link
            session['websocket_sid'] = websocket_sid
            session['last_activity'] = datetime.utcnow()
            self.websocket_to_session[websocket_sid] = session_id
            
        logger.info(f"WebSocket {websocket_sid} linked to session {session_id}")
        return True
    
    def unlink_websocket(self, websocket_sid: str) -> Optional[str]:
        """Unlink a WebSocket connection."""
        with self.lock:
            session_id = self.websocket_to_session.pop(websocket_sid, None)
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                if session['websocket_sid'] == websocket_sid:
                    session['websocket_sid'] = None
                    session['last_activity'] = datetime.utcnow()
            
        if session_id:
            logger.info(f"WebSocket {websocket_sid} unlinked from session {session_id}")
        return session_id
    
    def get_websocket_for_session(self, session_id: str) -> Optional[str]:
        """Get the WebSocket SID for a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and self._is_session_valid(session):
                session['last_activity'] = datetime.utcnow()
                return session['websocket_sid']
        return None
    
    def get_session_for_websocket(self, websocket_sid: str) -> Optional[str]:
        """Get the session ID for a WebSocket connection."""
        with self.lock:
            return self.websocket_to_session.get(websocket_sid)
    
    def add_http_request(self, session_id: str, request_id: str) -> bool:
        """Add an HTTP request to a session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and self._is_session_valid(session):
                session['last_activity'] = datetime.utcnow()
                return True
        return False
    
    def get_active_sessions(self) -> Dict:
        """Get information about active sessions."""
        with self.lock:
            active_sessions = []
            for session_id, session in self.sessions.items():
                if session['is_active'] and self._is_session_valid(session):
                    active_sessions.append({
                        'session_id': session_id,
                        'websocket_connected': session['websocket_sid'] is not None,
                        'websocket_sid': session['websocket_sid']
                    })
            
            return {
                'count': len(active_sessions),
                'sessions': active_sessions,
                'websocket_links': len(self.websocket_to_session)
            }
    
    def _is_session_valid(self, session: Dict) -> bool:
        """Check if a session is still valid."""
        if not session['is_active']:
            return False
        age = (datetime.utcnow() - session['last_activity']).total_seconds()
        return age < self.session_timeout

# Global session manager instance
session_manager = SessionManager()