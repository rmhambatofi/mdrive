from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth = Blueprint('auth', __name__)


class AuthController:
    @staticmethod
    @auth.route('/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing username or password'}), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        
        # Check if user already exists
        if AuthService.get_user_by_username(username):
            return jsonify({'message': 'User already exists'}), 400
        
        # Create new user
        user = AuthService.create_user(username, password, email, firstname, lastname)
        if not user:
            return jsonify({'message': 'Error creating user'}), 500
        
        return jsonify({'message': 'User created successfully'}), 201

    @staticmethod
    @auth.route('/login', methods=['POST'])
    def login():
        """Login and get access token"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing username or password'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Check if user exists
        if not AuthService.get_user_by_username(username):
            return jsonify({'message': 'User not found'}), 404
        
        # Authenticate user
        user = AuthService.authenticate_user(username, password)
        if not user:
            return jsonify({'message': 'Invalid password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        # Get token expiration from app config
        from flask import current_app
        expires_in_seconds = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        expires_in_hours = expires_in_seconds // 3600
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username,
            'token_expires_in': {
                'seconds': expires_in_seconds,
                'hours': expires_in_hours
            }
        }), 200

    @staticmethod
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
            'username': user.username,
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname
        }), 200

    @staticmethod
    @auth.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Logout user"""
        # In a production environment, you would typically add the token to a blocklist
        # or implement token revocation using Flask-JWT-Extended's token_in_blocklist_loader
        # For now, we'll just return a success message
        return jsonify({'message': 'Successfully logged out'}), 200
        
    @staticmethod
    @auth.route('/delete', methods=['DELETE'])
    @jwt_required()
    def delete_user():
        """Delete current user and all associated data"""
        current_user_id = get_jwt_identity()
        
        # Delete the user and all associated data
        result = AuthService.delete_user(current_user_id)
        
        if not result:
            return jsonify({'message': 'Error deleting user'}), 500
            
        return jsonify({'message': 'User and all associated data deleted successfully'}), 200