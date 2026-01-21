"""
Authentication routes module.
Defines URL endpoints for authentication operations.
"""
from flask import Blueprint
from app.controllers.auth_controller import AuthController

# Create blueprint
auth_bp = Blueprint('auth', __name__)


# Route definitions
@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register - Register a new user"""
    return AuthController.register()


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login - Login user"""
    return AuthController.login()


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """GET /api/auth/profile - Get current user profile"""
    return AuthController.get_profile()


@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """PUT /api/auth/profile - Update current user profile"""
    return AuthController.update_profile()
