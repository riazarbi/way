"""Background task processor for asynchronous LLM analysis."""

import uuid
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import queue
from .ollama_client import OllamaClient
from .message_queue import message_queue, Priority

logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """Handles asynchronous processing of hypothesis analysis tasks."""
    
    def __init__(self, max_workers: int = 4):  # Increased workers for concurrency
        self.max_workers = max_workers
        self.task_queue = queue.PriorityQueue()  # Priority queue for urgent tasks
        self.active_tasks = {}
        self.stats = {'queued': 0, 'processed': 0, 'failed': 0, 'cache_hits': 0}
        self.running = False
        self.workers = []
        self.lock = threading.Lock()
        
        # Performance optimizations
        self._ollama_clients = {}  # Worker-specific clients to avoid contention
        self._processing_timeout = 15  # Max processing time per task
        
    def start(self):
        """Start the background processing workers."""
        if not self.running:
            self.running = True
            for i in range(self.max_workers):
                worker = threading.Thread(target=self._worker, daemon=True, name=f"BgProcessor-{i}")
                worker.start()
                self.workers.append(worker)
            logger.info(f"Background processor started with {self.max_workers} workers")
    
    def stop(self):
        """Stop all background processing workers."""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=2)
        self.workers.clear()
        logger.info("Background processor stopped")
    
    def queue_hypothesis_analysis(self, processing_data: Dict[str, Any], priority: int = 1) -> str:
        """Queue a hypothesis analysis task for background processing with priority."""
        task_id = str(uuid.uuid4())
        
        task = {
            'id': task_id,
            'type': 'hypothesis_analysis',
            'data': processing_data,
            'created_at': datetime.utcnow(),
            'retries': 0,
            'priority': priority
        }
        
        with self.lock:
            self.active_tasks[task_id] = task
            self.stats['queued'] += 1
            
        # Use priority queue with tuple (priority, timestamp, task)
        self.task_queue.put((priority, time.time(), task))
        logger.debug(f"Task queued for analysis: {task_id} (priority: {priority})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        with self.lock:
            return self.active_tasks.get(task_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        with self.lock:
            return {
                'queue_size': self.task_queue.qsize(),
                'active_tasks': len(self.active_tasks),
                'stats': self.stats.copy(),
                'workers': len(self.workers),
                'running': self.running
            }
    
    def _worker(self):
        """Background worker thread for processing tasks."""
        worker_id = threading.current_thread().name
        
        # Create worker-specific Ollama client to avoid contention
        self._ollama_clients[worker_id] = OllamaClient()
        
        while self.running:
            try:
                # Get task with timeout to allow graceful shutdown
                priority, timestamp, task = self.task_queue.get(timeout=1.0)
                self._process_task(task, worker_id)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                time.sleep(0.5)  # Shorter sleep for faster recovery
    
    def _process_task(self, task: Dict[str, Any], worker_id: str):
        """Process a single background task with timeout and worker-specific client."""
        task_id = task['id']
        task_type = task['type']
        
        start_time = time.time()
        
        try:
            logger.debug(f"Worker {worker_id} processing task {task_id} of type {task_type}")
            
            if task_type == 'hypothesis_analysis':
                self._process_hypothesis_analysis(task, worker_id)
            else:
                logger.error(f"Unknown task type: {task_type}")
                self._mark_task_failed(task_id, f"Unknown task type: {task_type}")
                return
                
            processing_time = time.time() - start_time
            logger.debug(f"Task {task_id} processed in {processing_time:.3f}s by {worker_id}")
                
            with self.lock:
                self.stats['processed'] += 1
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                    
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Task processing failed {task_id} after {processing_time:.3f}s: {e}")
            self._handle_task_failure(task, str(e))
    
    def _process_hypothesis_analysis(self, task: Dict[str, Any], worker_id: str):
        """Process hypothesis analysis task with worker-specific client."""
        data = task['data']
        request_id = data['request_id']
        session_id = data['session_id']
        
        try:
            # Use worker-specific Ollama client to avoid contention
            ollama_client = self._ollama_clients.get(worker_id)
            if not ollama_client:
                logger.error(f"No Ollama client for worker {worker_id}")
                raise Exception(f"No Ollama client available for worker {worker_id}")
            
            # Perform LLM analysis with timing
            analysis_start = time.time()
            analysis = ollama_client.analyze_hypothesis(data['hypothesis'])
            analysis_time = time.time() - analysis_start
            
            # Track cache performance
            if analysis and 'response_time_ms' in analysis:
                if analysis['response_time_ms'] < 50:  # Likely a cache hit
                    with self.lock:
                        self.stats['cache_hits'] += 1
            
            # Prepare feedback data for WebSocket delivery
            feedback_data = {
                'message': 'Hypothesis analysis complete',
                'request_id': request_id,
                'status': 'analyzed',
                'timestamp': datetime.utcnow().isoformat(),
                'processing_time_ms': int(analysis_time * 1000),
                'worker_id': worker_id,
                'data': {
                    'hypothesis': data['hypothesis'],
                    'context': data.get('context', ''),
                    'metric': data.get('metric', '')
                },
                'analysis': analysis
            }
            
            # Send results via WebSocket if session exists
            if session_id:
                try:
                    message_id = message_queue.queue_message(
                        session_id=session_id,
                        event='hypothesis_feedback',
                        data=feedback_data,
                        priority=Priority.HIGH
                    )
                    logger.info(f"Analysis results queued for session {session_id}: {message_id}")
                except Exception as e:
                    logger.error(f"Failed to queue analysis results: {e}")
                    raise
            
            logger.info(f"Hypothesis analysis completed: {request_id}")
            
        except Exception as e:
            # Send error notification via WebSocket
            if session_id:
                try:
                    error_data = {
                        'request_id': request_id,
                        'status': 'error',
                        'message': 'Analysis failed',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    message_queue.queue_message(
                        session_id=session_id,
                        event='hypothesis_error',
                        data=error_data,
                        priority=Priority.HIGH
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to send error notification: {notification_error}")
            raise
    
    def _handle_task_failure(self, task: Dict[str, Any], error_msg: str):
        """Handle task processing failure with retry logic."""
        task_id = task['id']
        task['retries'] += 1
        
        if task['retries'] < 3:
            # Retry the task
            logger.warning(f"Retrying task {task_id} (attempt {task['retries']})")
            self.task_queue.put(task)
        else:
            # Mark as permanently failed
            logger.error(f"Task {task_id} failed permanently after 3 attempts")
            self._mark_task_failed(task_id, error_msg)
    
    def _mark_task_failed(self, task_id: str, error_msg: str):
        """Mark a task as permanently failed."""
        with self.lock:
            self.stats['failed'] += 1
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'failed'
                self.active_tasks[task_id]['error'] = error_msg
                # Keep failed tasks for a while for debugging
                # They'll be cleaned up by periodic cleanup if needed


# Global instance
background_processor = BackgroundProcessor()