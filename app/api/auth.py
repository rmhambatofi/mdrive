from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Check if user already exists
    if AuthService.get_user_by_username(username):
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new user
    user = AuthService.create_user(username, password)
    if not user:
        return jsonify({'message': 'Error creating user'}), 500
    
    return jsonify({'message': 'User created successfully'}), 201


@auth.route('/login', methods=['POST'])
def login():
    """Login and get access token"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Authenticate user
    user = AuthService.authenticate_user(username, password)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user_id': user.id,
        'username': user.username
    }), 200


@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username
    }), 200


@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    # In a production environment, you would typically add the token to a blocklist
    # or implement token revocation using Flask-JWT-Extended's token_in_blocklist_loader
    # For now, we'll just return a success message
    return jsonify({'message': 'Successfully logged out'}), 200