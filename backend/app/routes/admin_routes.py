"""
Admin routes module.
Defines URL endpoints for administration operations.
"""
from flask import Blueprint
from app.controllers.admin_controller import AdminController
from app.controllers.settings_controller import SettingsController

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
def list_users():
    """GET /api/admin/users - List all users"""
    return AdminController.list_users()


@admin_bp.route('/users/<user_uuid>/role', methods=['PUT'])
def update_user_role(user_uuid):
    """PUT /api/admin/users/<uuid>/role - Update a user's role"""
    return AdminController.update_user_role(user_uuid)


@admin_bp.route('/users/<user_uuid>/active', methods=['PUT'])
def toggle_user_active(user_uuid):
    """PUT /api/admin/users/<uuid>/active - Toggle user active status"""
    return AdminController.toggle_user_active(user_uuid)


@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """GET /api/admin/settings - Get application settings"""
    return SettingsController.get_settings()


@admin_bp.route('/settings', methods=['PUT'])
def update_settings():
    """PUT /api/admin/settings - Update application settings"""
    return SettingsController.update_settings()
