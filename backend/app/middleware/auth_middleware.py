"""
Authentication middleware module.
Provides JWT authentication decorators and utilities.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User, UserRole


def jwt_required_custom(fn):
    """
    Custom JWT required decorator with user loading.

    Args:
        fn: Function to wrap

    Returns:
        Wrapped function that requires valid JWT
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_uuid = get_jwt_identity()

            user = User.query.get(user_uuid)
            if not user:
                return jsonify({'error': 'User not found'}), 401

            if not user.is_active:
                return jsonify({'error': 'Account deactivated'}), 403

            return fn(user, *args, **kwargs)

        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401

    return wrapper


def admin_required(fn):
    """
    Admin-only decorator. Requires a valid JWT and ADMIN role.

    Args:
        fn: Function to wrap

    Returns:
        Wrapped function that requires ADMIN role
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_uuid = get_jwt_identity()

            user = User.query.get(user_uuid)
            if not user:
                return jsonify({'error': 'User not found'}), 401

            if user.role != UserRole.ADMIN:
                return jsonify({'error': 'Admin access required'}), 403

            return fn(user, *args, **kwargs)

        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401

    return wrapper


def get_current_user():
    """
    Get current authenticated user.

    Returns:
        User: Current user object or None
    """
    try:
        verify_jwt_in_request()
        user_uuid = get_jwt_identity()
        return User.query.get(user_uuid)
    except:
        return None
