"""
Admin controller module.
Handles HTTP requests for administration operations.
"""
from flask import request, jsonify
from app.middleware.auth_middleware import admin_required
from app.services.admin_service import AdminService


class AdminController:
    """Controller for admin endpoints."""

    @staticmethod
    @admin_required
    def list_users(admin):
        """
        List all users with stats.

        Requires: JWT token with ADMIN role

        Returns:
            JSON response with users list and summary stats
        """
        try:
            success, response_data, status_code = AdminService.list_users()
            return jsonify(response_data), status_code
        except Exception as e:
            return jsonify({'error': 'Failed to list users', 'details': str(e)}), 500

    @staticmethod
    @admin_required
    def update_user_role(admin, user_uuid):
        """
        Update a user's role.

        Requires: JWT token with ADMIN role
        Args:
            user_uuid (str): Target user UUID

        Expected JSON body:
            { "role": "ADMIN" | "SUBSCRIBER" | "LIMITED_SUBSCRIBER" }

        Returns:
            JSON response with updated user data
        """
        try:
            data = request.get_json()
            if not data or not data.get('role'):
                return jsonify({'error': 'role is required'}), 400

            success, response_data, status_code = AdminService.update_user_role(
                admin_uuid=admin.uuid,
                target_uuid=user_uuid,
                new_role=data['role']
            )
            return jsonify(response_data), status_code
        except Exception as e:
            return jsonify({'error': 'Failed to update role', 'details': str(e)}), 500
