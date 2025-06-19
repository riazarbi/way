import pytest
import time


class TestWebSocketIntegration:
    
    def test_websocket_connection(self, socketio_client):
        received = socketio_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'connected'
        assert 'session_id' in received[0]['args'][0]
    
    def test_websocket_echo(self, socketio_client):
        socketio_client.get_received()
        
        test_message = "Hello WebSocket"
        socketio_client.emit('echo', test_message)
        
        received = socketio_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'echo_response'
        assert received[0]['args'][0]['original_message'] == test_message
    
    def test_ping_pong_heartbeat(self, socketio_client):
        socketio_client.get_received()
        
        socketio_client.emit('ping')
        received = socketio_client.get_received()
        
        assert len(received) == 1
        assert received[0]['name'] == 'pong'
        assert 'timestamp' in received[0]['args'][0]
    
    def test_multiple_concurrent_connections(self, app):
        clients = []
        try:
            for i in range(3):
                client = app.socketio.test_client(app)
                clients.append(client)
                received = client.get_received()
                assert received[0]['name'] == 'connected'
        finally:
            for client in clients:
                client.disconnect()
    
    def test_connection_handshake_performance(self, app):
        start_time = time.time()
        client = app.socketio.test_client(app)
        received = client.get_received()
        handshake_time = (time.time() - start_time) * 1000
        
        assert len(received) == 1
        assert handshake_time < 100
        client.disconnect()