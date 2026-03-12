"""
Application factory module.
Creates and configures the Flask application instance.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def setup_logging(app):
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE')

    # Set log level
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler (if LOG_FILE is configured)
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Rotating file handler: 10MB max, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level, logging.INFO))
        app.logger.addHandler(file_handler)

    # Stream handler for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(getattr(logging, log_level, logging.INFO))
    app.logger.addHandler(stream_handler)

    app.logger.info(f"Logging initialized - Level: {log_level}, File: {log_file or 'None'}")


def create_app(config_name=None):
    """
    Application factory function.

    Args:
        config_name (str|None): Configuration name ('development', 'production').
            When None (or 'default'), the value of the FLASK_ENV environment
            variable is used (defaults to 'development').

    Returns:
        Flask: Configured Flask application instance
    """
    if not config_name or config_name == 'default':
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))

    # Setup logging
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS with full options for preflight requests
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        expose_headers=['Content-Type', 'Authorization']
    )

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.logger.info(f"Application created with config: {config_name}")
    app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    app.logger.info(f"CORS origins: {app.config['CORS_ORIGINS']}")

    # Import models so Flask-Migrate can detect all tables
    from app.models import user, file, setting  # noqa: F401

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.file_routes import file_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(file_bp, url_prefix='/api/files')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Register CLI commands
    from app.cli import create_admin_command
    app.cli.add_command(create_admin_command)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    return app
