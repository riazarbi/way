"""Connection manager unit and integration tests."""
import pytest
from app.connection_manager import ConnectionManager


class TestConnectionManager:
    """Test connection manager functionality."""
    
    def test_add_remove_connection(self, connection_manager, sample_connection_data):
        """Test adding and removing connections."""
        result = connection_manager.add_connection(
            sample_connection_data['sid'], sample_connection_data['user_id'])
        assert result is True
        assert connection_manager.total_connections == 1
        
        connection = connection_manager.get_connection(sample_connection_data['sid'])
        assert connection is not None
        assert connection.is_alive is True
        
        result = connection_manager.remove_connection(sample_connection_data['sid'])
        assert result is True
        assert connection_manager.get_connection(sample_connection_data['sid']) is None
    
    def test_connection_pool_limit(self):
        """Test connection pool size limits."""
        manager = ConnectionManager(max_connections=2)
        assert manager.add_connection('sid1', 'user1') is True
        assert manager.add_connection('sid2', 'user2') is True
        assert manager.add_connection('sid3', 'user3') is False
    
    def test_ping_pong_updates(self, connection_manager, sample_connection_data):
        """Test ping/pong timestamp updates."""
        connection_manager.add_connection(sample_connection_data['sid'])
        
        connection_manager.update_ping(sample_connection_data['sid'])
        connection = connection_manager.get_connection(sample_connection_data['sid'])
        assert connection.last_ping is not None
        
        connection_manager.update_pong(sample_connection_data['sid'])
        connection = connection_manager.get_connection(sample_connection_data['sid'])
        assert connection.last_pong is not None
    
    def test_connection_lifecycle(self, connection_manager):
        """Test connection lifecycle management."""
        connection_manager.add_connection('alive_sid')
        connection_manager.add_connection('dead_sid')
        connection_manager.mark_connection_dead('dead_sid')
        
        active_info = connection_manager.get_active_connections()
        assert active_info['count'] == 1
        
        cleaned = connection_manager.cleanup_dead_connections()
        assert 'dead_sid' in cleaned
        assert connection_manager.get_connection('dead_sid') is None
    
    def test_heartbeat_monitor(self):
        """Test heartbeat monitor functionality."""
        manager = ConnectionManager(heartbeat_interval=1)
        manager.start_heartbeat_monitor()
        assert manager.running is True
        assert manager.heartbeat_thread.is_alive()
        manager.stop_heartbeat_monitor()
        assert manager.running is False