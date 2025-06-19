import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024  # 16KB max request size
    

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
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