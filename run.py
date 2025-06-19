#!/usr/bin/env python3
"""Development server startup script."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use SocketIO's run method for WebSocket support
    app.socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)