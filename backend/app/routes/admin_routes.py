"""
Admin routes module.
Defines URL endpoints for administration operations.
"""
from flask import Blueprint
from app.controllers.admin_controller import AdminController

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
def list_users():
    """GET /api/admin/users - List all users"""
    return AdminController.list_users()


@admin_bp.route('/users/<user_uuid>/role', methods=['PUT'])
def update_user_role(user_uuid):
    """PUT /api/admin/users/<uuid>/role - Update a user's role"""
    return AdminController.update_user_role(user_uuid)
