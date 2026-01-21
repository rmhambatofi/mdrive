"""
Passenger WSGI entry point for cPanel deployment.
This file is required for Python applications on cPanel with Passenger.
"""
import sys
import os
from datetime import datetime

# Get the directory of this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the application directory to the Python path
sys.path.insert(0, CURRENT_DIR)

# Setup early logging for startup errors
LOG_DIR = os.path.join(CURRENT_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

def log_startup_message(message, level='INFO'):
    """Write a message to the log file during startup."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] {level} in passenger_wsgi: {message}\n")
    except Exception:
        pass  # Ignore logging errors during startup

log_startup_message("Starting MDrive application...")
log_startup_message(f"Python version: {sys.version}")
log_startup_message(f"Current directory: {CURRENT_DIR}")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(CURRENT_DIR, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        log_startup_message(f"Loaded .env from {env_path}")
    else:
        log_startup_message(f".env file not found at {env_path}", 'WARNING')
except ImportError:
    log_startup_message("python-dotenv not installed, using system environment", 'WARNING')

# Import and create the Flask application
try:
    from app import create_app

    # Create the application instance
    # Passenger expects an 'application' callable
    application = create_app('production')
    log_startup_message("Application created successfully")

except Exception as e:
    # If app fails to start, log the error and create a minimal WSGI app
    import traceback
    error_message = traceback.format_exc()
    log_startup_message(f"Application failed to start: {error_message}", 'ERROR')

    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = f"Application failed to start:\n\n{error_message}".encode('utf-8')
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
