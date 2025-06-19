import gc
import psutil
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass 
class ProductionConfig:
    """Production configuration with 8GB memory constraint."""
    memory_limit_mb: int = 7500
    warning_threshold_mb: int = 6000
    cache_max_size: int = 750
    cache_ttl_seconds: int = 4800
    similarity_threshold: float = 0.85


class ProductionManager:
    """Lightweight production manager for memory and performance optimization."""
    
    def __init__(self, config: ProductionConfig = None):
        self.config = config or ProductionConfig()
        self.last_gc_time = time.time()
        
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory status."""
        try:
            process = psutil.Process()
            process_mb = process.memory_info().rss / (1024 * 1024)
            system_memory = psutil.virtual_memory()
            
            within_limits = process_mb < self.config.memory_limit_mb
            pressure_level = self._get_pressure_level(process_mb)
            
            return {
                'process_memory_mb': process_mb,
                'system_available_mb': system_memory.available / (1024 * 1024),
                'within_limits': within_limits,
                'pressure_level': pressure_level,
                'timestamp': time.time()
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': time.time()}
    
    def _get_pressure_level(self, process_mb: float) -> str:
        """Get memory pressure level."""
        if process_mb >= self.config.memory_limit_mb * 0.93:
            return 'critical'
        elif process_mb >= self.config.warning_threshold_mb:
            return 'high'
        elif process_mb >= self.config.warning_threshold_mb * 0.8:
            return 'medium'
        else:
            return 'low'
    
    def maybe_cleanup(self) -> Dict[str, Any]:
        """Perform cleanup if memory pressure is high."""
        status = self.get_memory_status()
        
        if status.get('pressure_level') in ['high', 'critical']:
            # Force garbage collection
            collected = gc.collect()
            self.last_gc_time = time.time()
            
            return {
                'cleanup_performed': True,
                'objects_collected': collected,
                'timestamp': time.time()
            }
        
        return {'cleanup_performed': False, 'timestamp': time.time()}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Simple health check."""
        memory_status = self.get_memory_status()
        
        if 'error' in memory_status:
            status = 'unhealthy'
        elif memory_status.get('pressure_level') == 'critical':
            status = 'unhealthy'
        elif memory_status.get('pressure_level') == 'high':
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'memory': memory_status,
            'timestamp': time.time()
        }


# Global production manager instance
production_manager = ProductionManager()