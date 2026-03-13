"""
Authentication controller module.
Handles HTTP requests for authentication operations.
"""
from flask import request, jsonify
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import jwt_required_custom


class AuthController:
    """Controller for authentication endpoints."""

    @staticmethod
    def register():
        """
        Handle user registration request.

        Expected JSON body:
            {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }

        Returns:
            JSON response with user data and token
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            email = data.get('email')
            password = data.get('password')
            full_name = data.get('full_name')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            success, response_data, status_code = AuthService.register_user(
                email=email,
                password=password,
                full_name=full_name
            )

            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

    @staticmethod
    def login():
        """
        Handle user login request.

        Expected JSON body:
            {
                "email": "user@example.com",
                "password": "SecurePass123"
            }

        Returns:
            JSON response with user data and token
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            success, response_data, status_code = AuthService.login_user(
                email=email,
                password=password
            )

            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({'error': 'Login failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def get_profile(user):
        """
        Get current user profile.

        Requires: JWT token in Authorization header

        Returns:
            JSON response with user data
        """
        try:
            success, response_data, status_code = AuthService.get_user_profile(user.uuid)
            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def update_profile(user):
        """
        Update current user profile.

        Requires: JWT token in Authorization header
        Expected JSON body:
            {
                "full_name": "New Name"
            }

        Returns:
            JSON response with updated user data
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            full_name = data.get('full_name')

            success, response_data, status_code = AuthService.update_user_profile(
                user_uuid=user.uuid,
                full_name=full_name
            )

            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def change_password(user):
        """
        Change the authenticated user's password.

        Requires: JWT token in Authorization header
        Expected JSON body:
            {
                "current_password": "OldPass123",
                "new_password": "NewPass456"
            }

        Returns:
            JSON response with success message
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            current_password = data.get('current_password')
            new_password = data.get('new_password')

            if not current_password or not new_password:
                return jsonify({'error': 'current_password and new_password are required'}), 400

            success, response_data, status_code = AuthService.change_password(
                user_uuid=user.uuid,
                current_password=current_password,
                new_password=new_password,
            )

            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500
