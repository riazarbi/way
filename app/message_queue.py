"""Minimal message routing for WebSocket delivery."""

import json
import uuid
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from enum import Enum
import queue

logger = logging.getLogger(__name__)


class Priority(Enum):
    NORMAL = 2
    HIGH = 3


class MessageQueue:
    """Simple message queue with retry logic."""
    
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.queue = queue.PriorityQueue()
        self.retry_queue = queue.Queue()
        self.sent = {}
        self.stats = {'queued': 0, 'sent': 0, 'failed': 0}
        self.lock = threading.Lock()
        self.running = False
        self.worker = None
        self.app = None  # Store Flask app for context
        
    def start(self, app=None):
        if not self.running:
            self.running = True
            self.app = app  # Store app for context
            self.worker = threading.Thread(target=self._worker, daemon=True)
            self.worker.start()
            logger.info("Message queue started")
    
    def stop(self):
        self.running = False
        if self.worker:
            self.worker.join(timeout=2)
    
    def queue_message(self, session_id: str, event: str, data: Dict, 
                     priority: Priority = Priority.NORMAL) -> str:
        if self.queue.qsize() >= self.max_size:
            raise Exception("Queue full")
        
        msg_id = str(uuid.uuid4())
        message = {
            'id': msg_id,
            'session_id': session_id,
            'event': event,
            'data': {**data, '_message_id': msg_id},
            'created': datetime.utcnow(),
            'retries': 0
        }
        
        self.queue.put((priority.value, time.time(), message))
        self.stats['queued'] += 1
        return msg_id
    
    def confirm_delivery(self, msg_id: str) -> bool:
        with self.lock:
            if msg_id in self.sent:
                del self.sent[msg_id]
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'queue_size': self.queue.qsize(),
            'retry_queue_size': self.retry_queue.qsize(),
            'sent_pending': len(self.sent),
            'stats': self.stats.copy()
        }
    
    def _worker(self):
        while self.running:
            try:
                # Process main queue
                if not self.queue.empty():
                    _, _, message = self.queue.get_nowait()
                    self._send_message(message)
                
                # Process retries
                if not self.retry_queue.empty():
                    message = self.retry_queue.get_nowait()
                    if message['retries'] < 3:
                        self._send_message(message)
                    else:
                        self.stats['failed'] += 1
                
                time.sleep(0.1)
            except queue.Empty:
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1)
    
    def _send_message(self, message):
        try:
            from .session_manager import session_manager
            
            # Get WebSocket connection
            websocket_sid = session_manager.get_websocket_for_session(
                message['session_id']
            )
            
            if not websocket_sid:
                logger.debug(f"No WebSocket for session {message['session_id']}")
                self._retry_message(message)
                return
            
            # Use stored app context instead of current_app
            if not self.app:
                logger.error("No Flask app context available")
                self._retry_message(message)
                return
                
            with self.app.app_context():
                socketio = self.app.extensions.get('socketio')
                if socketio:
                    socketio.emit(message['event'], message['data'], 
                                room=websocket_sid)
                    
                    with self.lock:
                        self.sent[message['id']] = message
                    self.stats['sent'] += 1
                    
                    logger.info(f"Message sent: {message['id']} to session {message['session_id']}")
                else:
                    logger.error("SocketIO not found in app extensions")
                    self._retry_message(message)
                
        except Exception as e:
            logger.error(f"Send error: {e}")
            self._retry_message(message)
    
    def _retry_message(self, message):
        message['retries'] += 1
        if message['retries'] < 3:
            self.retry_queue.put(message)
        else:
            self.stats['failed'] += 1


# Global instance
message_queue = MessageQueue()