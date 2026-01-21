"""
File model module.
Defines the File database model for both files and folders.
"""
import uuid as uuid_lib
from datetime import datetime
from app import db


class File(db.Model):
    """File model representing both files and folders in the system."""

    __tablename__ = 'files'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    parent_folder_uuid = db.Column(db.String(36), db.ForeignKey('files.uuid', ondelete='CASCADE'), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Relative path from userdata
    file_size = db.Column(db.BigInteger, default=0)
    mime_type = db.Column(db.String(100))
    is_folder = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for folder hierarchy
    children = db.relationship('File',
                               backref=db.backref('parent', remote_side=[uuid]),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        db.Index('idx_user_parent', 'user_uuid', 'parent_folder_uuid'),
        db.Index('idx_user_folder', 'user_uuid', 'is_folder'),
    )

    def __init__(self, user_uuid, file_name, file_path, is_folder=False,
                 parent_folder_uuid=None, file_size=0, mime_type=None):
        """
        Initialize a new file or folder entry.

        Args:
            user_uuid (str): UUID of the file owner
            file_name (str): Name of the file/folder
            file_path (str): Relative storage path
            is_folder (bool): Whether this is a folder
            parent_folder_uuid (str, optional): Parent folder UUID
            file_size (int): Size in bytes (0 for folders)
            mime_type (str, optional): MIME type of the file
        """
        self.user_uuid = user_uuid
        self.file_name = file_name
        self.file_path = file_path
        self.is_folder = is_folder
        self.parent_folder_uuid = parent_folder_uuid
        self.file_size = file_size
        self.mime_type = mime_type

    def to_dict(self, include_children=False):
        """
        Convert file object to dictionary.

        Args:
            include_children (bool): Whether to include child items

        Returns:
            dict: File data dictionary
        """
        data = {
            'id': self.uuid,
            'user_id': self.user_uuid,
            'parent_folder_id': self.parent_folder_uuid,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'is_folder': self.is_folder,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_children and self.is_folder:
            data['children'] = [child.to_dict() for child in self.children.all()]

        return data

    def get_breadcrumb(self):
        """
        Get the breadcrumb path for this file/folder.

        Returns:
            list: List of parent folders from root to current
        """
        breadcrumb = []
        current = self
        while current:
            breadcrumb.insert(0, {
                'id': current.uuid,
                'name': current.file_name,
                'is_folder': current.is_folder
            })
            current = current.parent
        return breadcrumb

    def __repr__(self):
        return f'<File {self.file_name} ({"folder" if self.is_folder else "file"})>'
