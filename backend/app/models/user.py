"""
User model module.
Defines the User database model and related methods.
"""
import enum
import uuid as uuid_lib
from datetime import datetime
from app import db
import bcrypt


class UserRole(enum.Enum):
    """Enumeration of available user roles."""
    ADMIN = 'ADMIN'
    SUBSCRIBER = 'SUBSCRIBER'
    LIMITED_SUBSCRIBER = 'LIMITED_SUBSCRIBER'


class User(db.Model):
    """User model for authentication and file ownership."""

    __tablename__ = 'users'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.LIMITED_SUBSCRIBER)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    storage_used = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, email: str, password: str, full_name: str = None,
                 role: 'UserRole' = None):
        """
        Initialize a new user.

        Args:
            email (str): User email address
            password (str): Plain text password (will be hashed)
            full_name (str, optional): User's full name
            role (UserRole, optional): User role (default: LIMITED_SUBSCRIBER)
        """
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.role = role or UserRole.LIMITED_SUBSCRIBER
        self.is_active = True

    @property
    def storage_quota(self) -> int:
        """
        Storage quota derived from global settings based on user role.
        Cached on Flask's request context (g) to avoid repeated DB hits
        when serialising multiple users in the same request.

        Returns:
            int: Quota in bytes
        """
        from app.models.setting import Setting
        try:
            from flask import g
            if not hasattr(g, '_app_settings'):
                g._app_settings = Setting.get()
            settings = g._app_settings
        except RuntimeError:
            # Outside a request context (e.g. CLI commands)
            settings = Setting.get()

        if self.role == UserRole.ADMIN:
            return settings.admin_quota
        if self.role == UserRole.SUBSCRIBER:
            return settings.subscriber_quota
        return settings.limited_subscriber_quota

    def set_password(self, password: str) -> None:
        """
        Hash and set user password.

        Args:
            password (str): Plain text password
        """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password (str): Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_storage: bool = True) -> dict:
        """
        Convert user object to dictionary.

        Args:
            include_storage (bool): Whether to include storage information

        Returns:
            dict: User data dictionary
        """
        data = {
            'id': self.uuid,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_storage:
            quota = self.storage_quota
            data.update({
                'storage_quota': quota,
                'storage_used': self.storage_used,
                'storage_available': quota - self.storage_used
            })

        return data

    def __repr__(self):
        return f'<User {self.email}>'
