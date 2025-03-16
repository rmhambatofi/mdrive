import uuid
from datetime import datetime
import os

from flask import current_app

from app import db


class Folder(db.Model):
    """Modèle pour représenter un dossier dans le système de fichiers."""
    __tablename__ = 'folders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey('folders.id'), nullable=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relations
    parent = db.relationship('Folder', remote_side=[id], backref=db.backref('subfolders', lazy=True))
    owner = db.relationship('User', backref=db.backref('folders', lazy=True))
    files = db.relationship('File', backref=db.backref('folder', lazy=True),
                            primaryjoin="and_(Folder.id==File.folder_id, File.is_deleted==False)")

    def get_path(self):
        """Retourne le chemin complet du dossier."""
        if not self.parent:
            return '/' + self.name

        return os.path.join(self.parent.get_path(), self.name)

    def get_size(self):
        """Calcule la taille totale du dossier et de son contenu."""
        # Taille des fichiers dans ce dossier
        files_size = sum(file.size for file in self.files)

        # Taille des sous-dossiers
        subfolders_size = sum(subfolder.get_size() for subfolder in self.subfolders if not subfolder.is_deleted)

        return files_size + subfolders_size

    def __repr__(self):
        return f'<Folder {self.name}>'


class File(db.Model):
    """Modèle pour représenter un fichier dans le système."""
    __tablename__ = 'files'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(50), nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    size = db.Column(db.BigInteger, nullable=False)
    checksum = db.Column(db.String(128), nullable=True)  # Pour vérifier l'intégrité du fichier
    storage_path = db.Column(db.String(512), nullable=False)  # Chemin de stockage physique
    folder_id = db.Column(db.String(36), db.ForeignKey('folders.id'), nullable=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)

    # Relations
    owner = db.relationship('User', backref=db.backref('file_owners', lazy=True))

    @property
    def full_path(self):
        """Retourne le chemin complet du fichier."""
        if self.folder:
            return os.path.join(self.folder.get_path(), self.name)
        return '/' + self.name

    def get_physical_path(self):
        """Retourne le chemin physique complet du fichier."""
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.storage_path)

    def __repr__(self):
        return f'<File {self.name}>'


class FileVersion(db.Model):
    """Modèle pour gérer les versions d'un fichier."""
    __tablename__ = 'file_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = db.Column(db.String(36), db.ForeignKey('files.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    checksum = db.Column(db.String(128), nullable=True)
    storage_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.String(512), nullable=True)

    # Relations
    file = db.relationship('File', backref=db.backref('versions', lazy=True, order_by='FileVersion.version_number.desc()'))
    user = db.relationship('User', backref=db.backref('file_versions', lazy=True))

    def get_physical_path(self):
        """Retourne le chemin physique complet de la version du fichier."""
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.storage_path)

    def __repr__(self):
        return f'<FileVersion {self.file.name} v{self.version_number}>'
