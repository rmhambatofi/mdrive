"""
Setting model module.
Application-wide configuration stored as a singleton row.
"""
from datetime import datetime
from app import db

# Default quota values (in bytes)
DEFAULT_ADMIN_QUOTA = 50 * 1024 ** 3            # 50 GB
DEFAULT_SUBSCRIBER_QUOTA = 10 * 1024 ** 3       # 10 GB
DEFAULT_LIMITED_SUBSCRIBER_QUOTA = 1 * 1024 ** 3  # 1 GB


class Setting(db.Model):
    """
    Application settings — single-row singleton table.
    Use Setting.get() to access the current settings.
    """

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    admin_quota = db.Column(
        db.BigInteger, nullable=False, default=DEFAULT_ADMIN_QUOTA
    )
    subscriber_quota = db.Column(
        db.BigInteger, nullable=False, default=DEFAULT_SUBSCRIBER_QUOTA
    )
    limited_subscriber_quota = db.Column(
        db.BigInteger, nullable=False, default=DEFAULT_LIMITED_SUBSCRIBER_QUOTA
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @classmethod
    def get(cls) -> 'Setting':
        """
        Return the singleton settings row, creating it with defaults if absent.

        Returns:
            Setting: The application settings instance
        """
        instance = cls.query.first()
        if instance is None:
            instance = cls(
                admin_quota=DEFAULT_ADMIN_QUOTA,
                subscriber_quota=DEFAULT_SUBSCRIBER_QUOTA,
                limited_subscriber_quota=DEFAULT_LIMITED_SUBSCRIBER_QUOTA,
            )
            db.session.add(instance)
            db.session.commit()
        return instance

    def to_dict(self) -> dict:
        """Serialize settings to a dictionary."""
        return {
            'admin_quota': self.admin_quota,
            'subscriber_quota': self.subscriber_quota,
            'limited_subscriber_quota': self.limited_subscriber_quota,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
