from datetime import datetime
import os
from app import db

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_type = db.Column(db.String(100))
    is_folder = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = db.relationship('File', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    @property
    def extension(self):
        _, ext = os.path.splitext(self.original_filename)
        return ext.lower()[1:] if ext else ''
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'is_folder': self.is_folder,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }