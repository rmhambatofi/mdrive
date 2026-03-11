"""
Admin service module.
Business logic for administration operations.
"""
from flask import current_app
from app import db
from app.models.user import User, UserRole


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def list_users() -> tuple:
        """
        Retrieve all users with summary statistics.

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        users = User.query.order_by(User.created_at.desc()).all()

        stats = {
            'total': len(users),
            'admins': sum(1 for u in users if u.role == UserRole.ADMIN),
            'subscribers': sum(1 for u in users if u.role == UserRole.SUBSCRIBER),
            'limited_subscribers': sum(1 for u in users if u.role == UserRole.LIMITED_SUBSCRIBER),
        }

        return True, {
            'users': [u.to_dict() for u in users],
            'stats': stats
        }, 200

    @staticmethod
    def update_user_role(admin_uuid: str, target_uuid: str, new_role: str) -> tuple:
        """
        Change the role of a user.

        Args:
            admin_uuid (str): UUID of the admin performing the action
            target_uuid (str): UUID of the user to update
            new_role (str): New role value

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        # Validate role value
        valid_roles = {r.value for r in UserRole}
        if new_role not in valid_roles:
            return False, {
                'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }, 400

        user = User.query.get(target_uuid)
        if not user:
            return False, {'error': 'User not found'}, 404

        # Prevent an admin from demoting themselves
        if target_uuid == admin_uuid and UserRole[new_role] != UserRole.ADMIN:
            return False, {'error': 'You cannot change your own admin role'}, 403

        try:
            user.role = UserRole[new_role]
            db.session.commit()

            return True, {
                'message': f'Role updated to {new_role}',
                'user': user.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Role update error: {str(e)}")
            return False, {'error': 'Failed to update role', 'details': str(e)}, 500
