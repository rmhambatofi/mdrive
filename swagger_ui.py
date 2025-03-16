from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/openapi.yaml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "MDrive API Documentation"
    },
)

def register_swagger_ui(app):
    """Register Swagger UI blueprint to Flask app"""
    # Register blueprint at URL
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Add a route to serve the OpenAPI spec file
    @app.route('/static/openapi.yaml')
    def serve_swagger_spec():
        return app.send_static_file('openapi.yaml')

if __name__ == '__main__':
    # Create a simple Flask app for testing
    app = Flask(__name__)
    
    # Ensure the static folder exists and copy the OpenAPI spec there
    import os
    import shutil
    
    os.makedirs('static', exist_ok=True)
    shutil.copy('openapi.yaml', 'static/openapi.yaml')
    
    # Register Swagger UI
    register_swagger_ui(app)
    
    # Run the app
    app.run(host='0.0.0.0', port=5002, debug=True)