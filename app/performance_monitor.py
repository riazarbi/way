import time
import psutil
import threading
from collections import defaultdict, deque
from functools import wraps
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class PerformanceMonitor:
    """Lightweight performance monitoring system for real-time metrics collection."""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.metrics = defaultdict(lambda: deque(maxlen=max_history_size))
        self.counters = defaultdict(int)
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'response_time_ms': 200,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 80,
            'cache_hit_rate_percent': 70
        }
        
    def record_timing(self, name: str, duration_ms: float, metadata: Optional[Dict] = None):
        """Record a timing measurement."""
        with self.lock:
            timestamp = time.time()
            self.metrics[f'{name}_timing'].append({
                'timestamp': timestamp,
                'duration_ms': duration_ms,
                'metadata': metadata or {}
            })
            
            # Check threshold
            if name == 'end_to_end' and duration_ms > self.thresholds['response_time_ms']:
                self.record_alert(f'Response time threshold exceeded: {duration_ms}ms > {self.thresholds["response_time_ms"]}ms')
    
    def record_counter(self, name: str, value: int = 1):
        """Record a counter metric."""
        with self.lock:
            self.counters[name] += value
            timestamp = time.time()
            self.metrics[f'{name}_count'].append({
                'timestamp': timestamp,
                'value': self.counters[name]
            })
    
    def record_gauge(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Record a gauge metric."""
        with self.lock:
            timestamp = time.time()
            self.metrics[f'{name}_gauge'].append({
                'timestamp': timestamp,
                'value': value,
                'metadata': metadata or {}
            })
    
    def record_alert(self, message: str):
        """Record a performance alert."""
        with self.lock:
            timestamp = time.time()
            self.metrics['alerts'].append({
                'timestamp': timestamp,
                'message': message,
                'datetime': datetime.fromtimestamp(timestamp).isoformat()
            })
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics."""
        try:
            process = psutil.Process()
            system_cpu = psutil.cpu_percent(interval=None)
            system_memory = psutil.virtual_memory()
            process_memory = process.memory_info()
            
            metrics = {
                'cpu_usage_percent': system_cpu,
                'memory_usage_percent': system_memory.percent,
                'process_memory_mb': process_memory.rss / (1024 * 1024),
                'system_memory_available_mb': system_memory.available / (1024 * 1024),
                'timestamp': time.time()
            }
            
            # Record as gauge metrics
            for key, value in metrics.items():
                if key != 'timestamp':
                    self.record_gauge(f'system_{key}', value)
                    
                    # Check thresholds
                    if key in self.thresholds and value > self.thresholds[key]:
                        self.record_alert(f'{key} threshold exceeded: {value}% > {self.thresholds[key]}%')
            
            return metrics
        except Exception as e:
            return {'error': str(e), 'timestamp': time.time()}
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self.lock:
            summary = {
                'uptime_seconds': time.time() - self.start_time,
                'counters': dict(self.counters),
                'recent_metrics': {},
                'alerts': list(self.metrics['alerts'])[-10:],  # Last 10 alerts
                'thresholds': self.thresholds,
                'timestamp': time.time()
            }
            
            # Get recent values for timing metrics
            for key, values in self.metrics.items():
                if values and key.endswith('_timing'):
                    recent_values = list(values)[-10:]  # Last 10 measurements
                    if recent_values:
                        durations = [v['duration_ms'] for v in recent_values]
                        summary['recent_metrics'][key] = {
                            'avg_ms': sum(durations) / len(durations),
                            'max_ms': max(durations),
                            'min_ms': min(durations),
                            'count': len(recent_values)
                        }
            
            return summary


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def time_function(name: str, metadata_func=None):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metadata = metadata_func(*args, **kwargs) if metadata_func else None
                performance_monitor.record_timing(name, duration_ms, metadata)
        return wrapper
    return decorator


def record_timing(name: str, duration_ms: float, metadata: Optional[Dict] = None):
    """Convenience function to record timing."""
    performance_monitor.record_timing(name, duration_ms, metadata)


def record_counter(name: str, value: int = 1):
    """Convenience function to record counter."""
    performance_monitor.record_counter(name, value)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary including system metrics."""
    summary = performance_monitor.get_metrics_summary()
    summary['system'] = performance_monitor.get_system_metrics()
    return summary