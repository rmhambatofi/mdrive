"""
File service module.
Handles file and folder operations with database persistence.
"""
import os
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.file import File
from app.models.user import User
from app.services.storage_service import StorageService
from app.utils.validators import validate_filename, validate_file_size
from app.utils.helpers import get_mime_type, get_file_icon


class FileService:
    """Service class for file and folder operations."""

    @staticmethod
    def upload_file(user, file_object, parent_folder_uuid=None):
        """
        Upload a file for a user.

        Args:
            user (User): User object
            file_object: File object from request
            parent_folder_uuid (str, optional): Parent folder UUID

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        # Validate filename
        is_valid, sanitized_filename, error_msg = validate_filename(
            file_object.filename,
            current_app.config['ALLOWED_EXTENSIONS']
        )

        if not is_valid:
            return False, {'error': error_msg}, 400

        # Check file size (get approximate size from stream)
        file_object.seek(0, os.SEEK_END)
        file_size = file_object.tell()
        file_object.seek(0)

        is_valid, error_msg = validate_file_size(file_size, current_app.config['MAX_FILE_SIZE'])
        if not is_valid:
            return False, {'error': error_msg}, 400

        # Check storage quota
        if user.storage_used + file_size > user.storage_quota:
            return False, {'error': 'Storage quota exceeded'}, 403

        # Determine parent folder path
        parent_path = ""
        if parent_folder_uuid:
            parent_folder = File.query.filter_by(
                uuid=parent_folder_uuid,
                user_uuid=user.uuid,
                is_folder=True
            ).first()

            if not parent_folder:
                return False, {'error': 'Parent folder not found'}, 404

            parent_path = parent_folder.file_path

        # Generate relative file path
        relative_path = os.path.join(parent_path, sanitized_filename)

        # Check if file already exists
        existing_file = File.query.filter_by(
            user_uuid=user.uuid,
            file_path=relative_path
        ).first()

        if existing_file:
            return False, {'error': 'File already exists'}, 409

        try:
            # Save file to storage
            success, message, actual_size = StorageService.save_file(
                user.uuid,
                file_object,
                relative_path
            )

            if not success:
                return False, {'error': message}, 500

            # Get MIME type
            mime_type = get_mime_type(sanitized_filename)

            # Create database entry
            file_entry = File(
                user_uuid=user.uuid,
                file_name=sanitized_filename,
                file_path=relative_path,
                file_size=actual_size,
                mime_type=mime_type,
                is_folder=False,
                parent_folder_uuid=parent_folder_uuid
            )

            db.session.add(file_entry)

            # Update user storage
            user.storage_used += actual_size

            db.session.commit()

            return True, {
                'message': 'File uploaded successfully',
                'file': file_entry.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            # Try to clean up uploaded file
            StorageService.delete_file(user.uuid, relative_path)
            current_app.logger.error(f"File upload error: {str(e)}")
            return False, {'error': 'Upload failed', 'details': str(e)}, 500

    @staticmethod
    def get_files(user, parent_folder_uuid=None, page=1, per_page=50):
        """
        Get files and folders for a user.

        Args:
            user (User): User object
            parent_folder_uuid (str, optional): Parent folder UUID (None for root)
            page (int): Page number
            per_page (int): Items per page

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        try:
            query = File.query.filter_by(
                user_uuid=user.uuid,
                parent_folder_uuid=parent_folder_uuid
            ).order_by(File.is_folder.desc(), File.file_name)

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            files = [{
                **file.to_dict(),
                'icon': get_file_icon(file.mime_type, file.is_folder)
            } for file in pagination.items]

            # Get breadcrumb if in a folder
            breadcrumb = []
            if parent_folder_uuid:
                folder = File.query.get(parent_folder_uuid)
                if folder:
                    breadcrumb = folder.get_breadcrumb()

            return True, {
                'files': files,
                'breadcrumb': breadcrumb,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }, 200

        except Exception as e:
            current_app.logger.error(f"Get files error: {str(e)}")
            return False, {'error': 'Failed to retrieve files', 'details': str(e)}, 500

    @staticmethod
    def get_file_by_uuid(user, file_uuid):
        """
        Get a specific file by UUID.

        Args:
            user (User): User object
            file_uuid (str): File UUID

        Returns:
            tuple: (success: bool, data: dict|File, status_code: int)
        """
        file = File.query.filter_by(uuid=file_uuid, user_uuid=user.uuid).first()

        if not file:
            return False, {'error': 'File not found'}, 404

        return True, file, 200

    @staticmethod
    def delete_file(user, file_uuid):
        """
        Delete a file or folder.

        Args:
            user (User): User object
            file_uuid (str): File UUID

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        file = File.query.filter_by(uuid=file_uuid, user_uuid=user.uuid).first()

        if not file:
            return False, {'error': 'File not found'}, 404

        try:
            # Calculate total size (including folder contents)
            total_size = FileService._calculate_size_recursive(file)

            # Delete from storage
            success, message = StorageService.delete_file(user.uuid, file.file_path)

            if not success:
                return False, {'error': message}, 500

            # Delete from database (cascade will delete children)
            db.session.delete(file)

            # Update user storage
            user.storage_used = max(0, user.storage_used - total_size)

            db.session.commit()

            return True, {'message': 'File deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"File delete error: {str(e)}")
            return False, {'error': 'Delete failed', 'details': str(e)}, 500

    @staticmethod
    def create_folder(user, folder_name, parent_folder_uuid=None):
        """
        Create a new folder.

        Args:
            user (User): User object
            folder_name (str): Name of the folder
            parent_folder_uuid (str, optional): Parent folder UUID

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        # Validate folder name
        is_valid, sanitized_name, error_msg = validate_filename(folder_name)

        if not is_valid:
            return False, {'error': error_msg}, 400

        # Determine parent folder path
        parent_path = ""
        if parent_folder_uuid:
            parent_folder = File.query.filter_by(
                uuid=parent_folder_uuid,
                user_uuid=user.uuid,
                is_folder=True
            ).first()

            if not parent_folder:
                return False, {'error': 'Parent folder not found'}, 404

            parent_path = parent_folder.file_path

        # Generate relative folder path
        relative_path = os.path.join(parent_path, sanitized_name)

        # Check if folder already exists
        existing_folder = File.query.filter_by(
            user_uuid=user.uuid,
            file_path=relative_path,
            is_folder=True
        ).first()

        if existing_folder:
            return False, {'error': 'Folder already exists'}, 409

        try:
            # Create folder in storage
            success, message = StorageService.create_folder(user.uuid, relative_path)

            if not success:
                return False, {'error': message}, 500

            # Create database entry
            folder = File(
                user_uuid=user.uuid,
                file_name=sanitized_name,
                file_path=relative_path,
                is_folder=True,
                parent_folder_uuid=parent_folder_uuid
            )

            db.session.add(folder)
            db.session.commit()

            return True, {
                'message': 'Folder created successfully',
                'folder': folder.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            StorageService.delete_file(user.uuid, relative_path)
            current_app.logger.error(f"Folder create error: {str(e)}")
            return False, {'error': 'Folder creation failed', 'details': str(e)}, 500

    @staticmethod
    def rename_file(user, file_uuid, new_name):
        """
        Rename a file or folder.

        Args:
            user (User): User object
            file_uuid (str): File UUID
            new_name (str): New name

        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        file = File.query.filter_by(uuid=file_uuid, user_uuid=user.uuid).first()

        if not file:
            return False, {'error': 'File not found'}, 404

        # Validate new name
        is_valid, sanitized_name, error_msg = validate_filename(new_name)

        if not is_valid:
            return False, {'error': error_msg}, 400

        try:
            # Generate new path
            parent_path = os.path.dirname(file.file_path)
            new_relative_path = os.path.join(parent_path, sanitized_name)

            # Check if name already exists
            existing = File.query.filter_by(
                user_uuid=user.uuid,
                file_path=new_relative_path
            ).first()

            if existing and existing.uuid != file_uuid:
                return False, {'error': 'Name already exists'}, 409

            # Move in storage
            success, message = StorageService.move_file(
                user.uuid,
                file.file_path,
                new_relative_path
            )

            if not success:
                return False, {'error': message}, 500

            # Update database
            old_path = file.file_path
            file.file_name = sanitized_name
            file.file_path = new_relative_path

            # Update children paths if folder
            if file.is_folder:
                FileService._update_children_paths(file, old_path, new_relative_path)

            db.session.commit()

            return True, {
                'message': 'File renamed successfully',
                'file': file.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"File rename error: {str(e)}")
            return False, {'error': 'Rename failed', 'details': str(e)}, 500

    @staticmethod
    def _calculate_size_recursive(file):
        """Calculate total size including folder contents."""
        if not file.is_folder:
            return file.file_size

        total = 0
        for child in file.children.all():
            total += FileService._calculate_size_recursive(child)

        return total

    @staticmethod
    def _update_children_paths(folder, old_path, new_path):
        """Recursively update paths for folder children."""
        for child in folder.children.all():
            child.file_path = child.file_path.replace(old_path, new_path, 1)
            if child.is_folder:
                FileService._update_children_paths(child, old_path, new_path)
