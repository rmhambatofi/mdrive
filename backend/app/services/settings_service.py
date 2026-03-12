"""
Settings service module.
Business logic for application-wide settings management.
"""
from flask import current_app
from app import db
from app.models.setting import Setting


class SettingsService:
    """Service class for settings operations."""

    @staticmethod
    def get_settings() -> tuple:
        """
        Retrieve current application settings.

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        settings = Setting.get()
        return True, {'settings': settings.to_dict()}, 200

    @staticmethod
    def update_settings(data: dict) -> tuple:
        """
        Update application settings.

        Args:
            data (dict): Fields to update. Accepted keys:
                - subscriber_quota (int): Bytes
                - limited_subscriber_quota (int): Bytes

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        settings = Setting.get()

        try:
            if 'admin_quota' in data:
                value = int(data['admin_quota'])
                if value <= 0:
                    return False, {'error': 'admin_quota must be a positive integer'}, 400
                settings.admin_quota = value

            if 'subscriber_quota' in data:
                value = int(data['subscriber_quota'])
                if value <= 0:
                    return False, {'error': 'subscriber_quota must be a positive integer'}, 400
                settings.subscriber_quota = value

            if 'limited_subscriber_quota' in data:
                value = int(data['limited_subscriber_quota'])
                if value <= 0:
                    return False, {'error': 'limited_subscriber_quota must be a positive integer'}, 400
                settings.limited_subscriber_quota = value

            db.session.commit()

            # Invalidate any cached settings that may exist in other contexts
            return True, {
                'message': 'Settings updated successfully',
                'settings': settings.to_dict()
            }, 200

        except (ValueError, TypeError):
            db.session.rollback()
            return False, {'error': 'Quota values must be valid integers'}, 400

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Settings update error: {str(e)}")
            return False, {'error': 'Failed to update settings', 'details': str(e)}, 500
