"""
Authentication service module.
Handles user registration, login, and authentication logic.
"""
import os
from flask import current_app
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from app.utils.helpers import ensure_directory_exists


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def register_user(email, password, full_name=None):
        """
        Register a new user.

        Args:
            email (str): User email
            password (str): User password
            full_name (str, optional): User's full name

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        # Validate email
        if not validate_email(email):
            return False, {'error': 'Invalid email format'}, 400

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return False, {'error': error_msg}, 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return False, {'error': 'Email already registered'}, 409

        try:
            # Create new user
            user = User(
                email=email,
                password=password,
                full_name=full_name,
            )

            db.session.add(user)
            db.session.commit()

            # Create user's root directory
            user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], user.uuid)
            if not ensure_directory_exists(user_dir):
                # Rollback if directory creation fails
                db.session.delete(user)
                db.session.commit()
                return False, {'error': 'Failed to create user storage directory'}, 500

            # Generate JWT token with UUID as identity
            access_token = create_access_token(identity=user.uuid)

            return True, {
                'message': 'User registered successfully',
                'user': user.to_dict(),
                'access_token': access_token
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            return False, {'error': 'Registration failed', 'details': str(e)}, 500

    @staticmethod
    def login_user(email, password):
        """
        Authenticate user and generate JWT token.

        Args:
            email (str): User email
            password (str): User password

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        # Validate inputs
        if not email or not password:
            return False, {'error': 'Email and password are required'}, 400

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return False, {'error': 'Invalid email or password'}, 401

        if not user.is_active:
            return False, {'error': 'Your account has been deactivated. Please contact an administrator.'}, 403

        try:
            # Generate JWT token with UUID as identity
            access_token = create_access_token(identity=user.uuid)

            return True, {
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token
            }, 200

        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return False, {'error': 'Login failed', 'details': str(e)}, 500

    @staticmethod
    def get_user_profile(user_uuid):
        """
        Get user profile information.

        Args:
            user_uuid (str): User UUID

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        user = User.query.get(user_uuid)

        if not user:
            return False, {'error': 'User not found'}, 404

        return True, {'user': user.to_dict()}, 200

    @staticmethod
    def update_user_profile(user_uuid, full_name=None):
        """
        Update user profile information.

        Args:
            user_uuid (str): User UUID
            full_name (str, optional): New full name

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        user = User.query.get(user_uuid)

        if not user:
            return False, {'error': 'User not found'}, 404

        try:
            if full_name is not None:
                user.full_name = full_name

            db.session.commit()

            return True, {
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profile update error: {str(e)}")
            return False, {'error': 'Profile update failed', 'details': str(e)}, 500

    @staticmethod
    def change_password(user_uuid: str, current_password: str, new_password: str) -> tuple:
        """
        Change a user's password after verifying the current one.

        Args:
            user_uuid (str): User UUID
            current_password (str): Current plain-text password
            new_password (str): New plain-text password

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        user = User.query.get(user_uuid)
        if not user:
            return False, {'error': 'User not found'}, 404

        if not user.check_password(current_password):
            return False, {'error': 'Current password is incorrect'}, 400

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return False, {'error': error_msg}, 400

        try:
            user.set_password(new_password)
            db.session.commit()
            return True, {'message': 'Password changed successfully'}, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password change error: {str(e)}")
            return False, {'error': 'Failed to change password', 'details': str(e)}, 500
