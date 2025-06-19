import pytest
from app import create_app
from app.connection_manager import ConnectionManager


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        yield app


@pytest.fixture  
def client(app):
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    return app.socketio.test_client(app)


@pytest.fixture
def connection_manager():
    return ConnectionManager(max_connections=5, heartbeat_interval=1)


@pytest.fixture
def sample_connection_data():
    return {
        'sid': 'test_session_123',
        'user_id': 'test_user_456', 
        'client_info': {'client_ip': '127.0.0.1'}
    }