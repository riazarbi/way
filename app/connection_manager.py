import threading
import time
import datetime
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""
    sid: str
    connected_at: datetime.datetime
    last_ping: Optional[datetime.datetime] = None
    last_pong: Optional[datetime.datetime] = None
    user_id: Optional[str] = None
    client_info: Dict = field(default_factory=dict)
    is_alive: bool = True

class ConnectionManager:
    """Manages WebSocket connection pool with health monitoring."""
    
    def __init__(self, max_connections: int = 100, heartbeat_interval: int = 30):
        self.max_connections = max_connections
        self.heartbeat_interval = heartbeat_interval
        self.connections: Dict[str, ConnectionInfo] = {}
        self.lock = threading.RLock()
        self.heartbeat_thread = None
        self.running = False
        self.total_connections = 0
        
    def start_heartbeat_monitor(self):
        """Start the heartbeat monitoring thread."""
        if self.heartbeat_thread is None or not self.heartbeat_thread.is_alive():
            self.running = True
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
            self.heartbeat_thread.start()
            logger.info("Connection heartbeat monitor started")
    
    def stop_heartbeat_monitor(self):
        """Stop the heartbeat monitoring thread."""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
            logger.info("Connection heartbeat monitor stopped")
    
    def add_connection(self, sid: str, user_id: Optional[str] = None, client_info: Optional[Dict] = None) -> bool:
        """Add a new connection to the pool."""
        with self.lock:
            if len(self.connections) >= self.max_connections:
                logger.warning(f"Connection pool full ({self.max_connections}), rejecting connection {sid}")
                return False
            
            if sid in self.connections:
                logger.warning(f"Connection {sid} already exists, updating")
            
            self.connections[sid] = ConnectionInfo(
                sid=sid,
                connected_at=datetime.datetime.utcnow(),
                user_id=user_id,
                client_info=client_info or {}
            )
            self.total_connections += 1
            
            logger.info(f"Connection added: {sid} (total: {len(self.connections)})")
            return True
    
    def remove_connection(self, sid: str) -> bool:
        """Remove a connection from the pool."""
        with self.lock:
            if sid in self.connections:
                connection = self.connections.pop(sid)
                duration = datetime.datetime.utcnow() - connection.connected_at
                logger.info(f"Connection removed: {sid} (duration: {duration.total_seconds():.1f}s, active: {len(self.connections)})")
                return True
            else:
                logger.warning(f"Attempted to remove non-existent connection: {sid}")
                return False
    
    def get_connection(self, sid: str) -> Optional[ConnectionInfo]:
        """Get connection information."""
        with self.lock:
            return self.connections.get(sid)
    
    def update_ping(self, sid: str):
        """Update last ping time for a connection."""
        with self.lock:
            if sid in self.connections:
                self.connections[sid].last_ping = datetime.datetime.utcnow()
    
    def update_pong(self, sid: str):
        """Update last pong time for a connection."""
        with self.lock:
            if sid in self.connections:
                self.connections[sid].last_pong = datetime.datetime.utcnow()
    
    def mark_connection_dead(self, sid: str):
        """Mark a connection as dead."""
        with self.lock:
            if sid in self.connections:
                self.connections[sid].is_alive = False
                logger.warning(f"Connection marked as dead: {sid}")
    
    def get_active_connections(self) -> Dict:
        """Get information about active connections."""
        with self.lock:
            active_connections = []
            for sid, conn in self.connections.items():
                if conn.is_alive:
                    active_connections.append({
                        'sid': sid,
                        'connected_at': conn.connected_at.isoformat(),
                        'user_id': conn.user_id,
                        'duration': (datetime.datetime.utcnow() - conn.connected_at).total_seconds(),
                        'last_ping': conn.last_ping.isoformat() if conn.last_ping else None,
                        'last_pong': conn.last_pong.isoformat() if conn.last_pong else None
                    })
            
            return {
                'count': len(active_connections),
                'max_connections': self.max_connections,
                'total_connections_served': self.total_connections,
                'connections': active_connections
            }
    
    def get_stale_connections(self, timeout_seconds: int = 60) -> List[str]:
        """Get list of connections that haven't responded to ping in timeout_seconds."""
        stale_connections = []
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=timeout_seconds)
        
        with self.lock:
            for sid, conn in self.connections.items():
                # Check if connection has ping without recent pong
                if conn.last_ping:
                    if not conn.last_pong or conn.last_pong < conn.last_ping:
                        if conn.last_ping < cutoff_time:
                            stale_connections.append(sid)
                    elif conn.last_pong < cutoff_time:
                        # Both ping and pong exist but pong is too old
                        stale_connections.append(sid)
                else:
                    # Connection that never received a ping - check age
                    if conn.connected_at < cutoff_time:
                        stale_connections.append(sid)
        
        return stale_connections
    
    def cleanup_dead_connections(self) -> List[str]:
        """Remove dead connections from the pool."""
        dead_connections = []
        with self.lock:
            for sid, conn in list(self.connections.items()):
                if not conn.is_alive:
                    dead_connections.append(sid)
                    self.connections.pop(sid)
        
        if dead_connections:
            logger.info(f"Cleaned up {len(dead_connections)} dead connections")
        
        return dead_connections
    
    def _heartbeat_monitor(self):
        """Background thread for monitoring connection health."""
        logger.info("Heartbeat monitor thread started")
        
        while self.running:
            try:
                # Get current time
                now = datetime.datetime.utcnow()
                
                # Check for stale connections
                stale_connections = self.get_stale_connections(timeout_seconds=30)
                
                if stale_connections:
                    logger.info(f"Found {len(stale_connections)} stale connections")
                    for sid in stale_connections:
                        self.mark_connection_dead(sid)
                
                # Clean up dead connections
                self.cleanup_dead_connections()
                
                # Log connection pool status periodically
                if len(self.connections) > 0:
                    active_info = self.get_active_connections()
                    logger.debug(f"Connection pool status: {active_info['count']} active connections")
                
                # Sleep for heartbeat interval
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                time.sleep(5)  # Short sleep before retrying
        
        logger.info("Heartbeat monitor thread stopped")

# Global connection manager instance
connection_manager = ConnectionManager()