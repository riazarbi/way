import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024  # 16KB max request size
    
    # Cache configuration (optimized based on load testing)
    CACHE_MAX_SIZE = int(os.environ.get('CACHE_MAX_SIZE', '500'))
    CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', '3600'))
    CACHE_SIMILARITY_THRESHOLD = float(os.environ.get('CACHE_SIMILARITY_THRESHOLD', '0.88'))
    
    # Memory management
    MEMORY_LIMIT_MB = int(os.environ.get('MEMORY_LIMIT_MB', '7500'))
    MEMORY_WARNING_MB = int(os.environ.get('MEMORY_WARNING_MB', '6000'))
    MEMORY_CRITICAL_MB = int(os.environ.get('MEMORY_CRITICAL_MB', '7000'))
    
    # Performance monitoring
    MONITOR_INTERVAL_SECONDS = int(os.environ.get('MONITOR_INTERVAL_SECONDS', '30'))
    ALERT_RESPONSE_TIME_MS = int(os.environ.get('ALERT_RESPONSE_TIME_MS', '200'))
    
    # Health check configuration
    HEALTH_CHECK_TIMEOUT_SECONDS = int(os.environ.get('HEALTH_CHECK_TIMEOUT_SECONDS', '5'))
    READINESS_CHECK_ENABLED = os.environ.get('READINESS_CHECK_ENABLED', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    
    # Less aggressive caching for development
    CACHE_MAX_SIZE = 100
    CACHE_TTL_SECONDS = 1800  # 30 minutes
    MEMORY_LIMIT_MB = 4000  # 4GB for development


class ProductionConfig(Config):
    """Production configuration with optimized parameters."""
    DEBUG = False
    ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production-optimized cache parameters (based on load testing results)
    CACHE_MAX_SIZE = 750  # Optimized for 65%+ hit rate
    CACHE_TTL_SECONDS = 4800  # 80 minutes for better retention
    CACHE_SIMILARITY_THRESHOLD = 0.85  # Balanced precision/recall
    
    # Strict memory limits for 8GB constraint
    MEMORY_LIMIT_MB = 7500  # 93.75% of 8GB
    MEMORY_WARNING_MB = 6000  # 75% warning
    MEMORY_CRITICAL_MB = 7000  # 87.5% critical
    
    # Production monitoring
    MONITOR_INTERVAL_SECONDS = 15  # More frequent monitoring
    ALERT_RESPONSE_TIME_MS = 180  # Stricter threshold
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environment")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    
    # Test-friendly settings
    CACHE_MAX_SIZE = 10
    CACHE_TTL_SECONDS = 60
    MEMORY_LIMIT_MB = 1000
    MONITOR_INTERVAL_SECONDS = 1