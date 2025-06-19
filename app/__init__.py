import logging
import os
from flask import Flask


def create_app(config_name=None):
    """Flask application factory."""
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    if config_name == 'development':
        app.config.from_object('app.config.DevelopmentConfig')
    elif config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Setup logging
    if not app.debug and not app.testing:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Initialize WebSocket support
    from app.websocket import create_socketio
    socketio = create_socketio(app)
    
    # Initialize message queue
    from app.message_queue import message_queue
    message_queue.start()
    
    # Initialize background processor
    from app.background_processor import background_processor
    background_processor.start()
    
    # Initialize production management
    from app.production_manager import production_manager, ProductionConfig
    from app.hypothesis_cache import hypothesis_cache
    
    # Configure production settings based on environment
    if app.config.get('ENV') == 'production':
        prod_config = ProductionConfig(
            memory_limit_mb=app.config.get('MEMORY_LIMIT_MB', 7500),
            warning_threshold_mb=app.config.get('MEMORY_WARNING_MB', 6000),
            cache_max_size=app.config.get('CACHE_MAX_SIZE', 750),
            cache_ttl_seconds=app.config.get('CACHE_TTL_SECONDS', 4800),
            similarity_threshold=app.config.get('CACHE_SIMILARITY_THRESHOLD', 0.85)
        )
        production_manager.config = prod_config
        
        # Configure cache with optimized parameters
        hypothesis_cache.configure(
            max_size=prod_config.cache_max_size,
            ttl_hours=prod_config.cache_ttl_seconds / 3600,
            similarity_threshold=prod_config.similarity_threshold
        )
    
    # Store socketio instance on app for access in other modules
    app.socketio = socketio
    
    # Store cleanup function for shutdown
    @app.teardown_appcontext
    def cleanup_message_router(error):
        if error:
            app.logger.error(f"Application context error: {error}")
    
    # Add proper shutdown handling
    import atexit
    def cleanup_on_shutdown():
        """Clean up resources on application shutdown."""
        try:
            message_queue.stop()
            background_processor.stop()
            app.logger.info("Application shutdown cleanup completed")
        except Exception as e:
            app.logger.error(f"Error during shutdown cleanup: {e}")
    
    atexit.register(cleanup_on_shutdown)
    
    return app