"""
Application configuration module.
Handles environment variables and application settings.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Priority order (highest → lowest):
#   1. System environment variables (e.g. cPanel "Environment variables", Docker, CI)
#   2. .env file (local development or server-side .env)
#   3. Hardcoded defaults below
# override=False ensures system env vars are NEVER overwritten by the .env file.
load_dotenv(override=False)


class Config:
    """Base configuration class."""

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'mdrive')
    DB_USER = os.getenv('DB_USER', 'mdrive_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'mdrive_password')

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-this')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 2684354560))  # 2.5GB
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE  # Flask built-in request body limiter
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  os.getenv('UPLOAD_FOLDER', 'userdata'))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS',
                                       'pdf,doc,docx,txt,png,jpg,jpeg,gif,zip,rar,mp4,mp3').split(','))

    # Storage Configuration
    DEFAULT_STORAGE_QUOTA = int(os.getenv('DEFAULT_STORAGE_QUOTA', 5368709120))  # 5GB

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Configuration dictionary
# 'default' auto-resolves based on FLASK_ENV (falls back to development)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig if os.getenv('FLASK_ENV') == 'production' else DevelopmentConfig,
}
