"""
Settings controller module.
Handles HTTP requests for application settings (ADMIN only).
"""
from flask import request, jsonify
from app.middleware.auth_middleware import admin_required
from app.services.settings_service import SettingsService


class SettingsController:
    """Controller for settings endpoints."""

    @staticmethod
    @admin_required
    def get_settings(admin):
        """
        Get current application settings.

        Requires: JWT token with ADMIN role

        Returns:
            JSON response with current settings
        """
        success, data, code = SettingsService.get_settings()
        return jsonify(data), code

    @staticmethod
    @admin_required
    def update_settings(admin):
        """
        Update application settings.

        Requires: JWT token with ADMIN role

        Expected JSON body (all fields optional):
            {
                "subscriber_quota": <bytes>,
                "limited_subscriber_quota": <bytes>
            }

        Returns:
            JSON response with updated settings
        """
        data = request.get_json() or {}
        success, response_data, code = SettingsService.update_settings(data)
        return jsonify(response_data), code
