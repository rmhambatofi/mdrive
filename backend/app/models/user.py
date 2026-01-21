"""
User model module.
Defines the User database model and related methods.
"""
import uuid as uuid_lib
from datetime import datetime
from app import db
import bcrypt


class User(db.Model):
    """User model for authentication and file ownership."""

    __tablename__ = 'users'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    storage_quota = db.Column(db.BigInteger, default=5368709120)  # 5GB default
    storage_used = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, email, password, full_name=None, storage_quota=None):
        """
        Initialize a new user.

        Args:
            email (str): User email address
            password (str): Plain text password (will be hashed)
            full_name (str, optional): User's full name
            storage_quota (int, optional): Storage quota in bytes
        """
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        if storage_quota:
            self.storage_quota = storage_quota

    def set_password(self, password):
        """
        Hash and set user password.

        Args:
            password (str): Plain text password
        """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """
        Verify password against stored hash.

        Args:
            password (str): Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_storage=True):
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_storage:
            data.update({
                'storage_quota': self.storage_quota,
                'storage_used': self.storage_used,
                'storage_available': self.storage_quota - self.storage_used
            })

        return data

    def __repr__(self):
        return f'<User {self.email}>'
