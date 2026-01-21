"""
Storage service module.
Handles physical file storage operations on the filesystem.
"""
import os
import shutil
from flask import current_app
from werkzeug.utils import secure_filename
from app.utils.validators import sanitize_path
from app.utils.helpers import ensure_directory_exists


class StorageService:
    """Service class for file storage operations."""

    @staticmethod
    def get_user_storage_path(user_uuid):
        """
        Get the root storage path for a user.

        Args:
            user_uuid (str): User's UUID

        Returns:
            str: Absolute path to user's storage directory
        """
        return os.path.join(current_app.config['UPLOAD_FOLDER'], user_uuid)

    @staticmethod
    def get_full_path(user_uuid, relative_path):
        """
        Get the full filesystem path for a file.

        Args:
            user_uuid (str): User's UUID
            relative_path (str): Relative path within user's storage

        Returns:
            str: Absolute filesystem path
        """
        user_path = StorageService.get_user_storage_path(user_uuid)
        sanitized_path = sanitize_path(relative_path)
        return os.path.join(user_path, sanitized_path)

    @staticmethod
    def save_file(user_uuid, file_object, relative_path):
        """
        Save an uploaded file to storage.

        Args:
            user_uuid (str): User's UUID
            file_object: File object from request
            relative_path (str): Relative path where file should be saved

        Returns:
            tuple: (success: bool, message: str, file_size: int)
        """
        try:
            full_path = StorageService.get_full_path(user_uuid, relative_path)

            # Ensure directory exists
            directory = os.path.dirname(full_path)
            if not ensure_directory_exists(directory):
                return False, "Failed to create storage directory", 0

            # Save file
            file_object.save(full_path)

            # Get file size
            file_size = os.path.getsize(full_path)

            return True, "File saved successfully", file_size

        except Exception as e:
            current_app.logger.error(f"File save error: {str(e)}")
            return False, f"Failed to save file: {str(e)}", 0

    @staticmethod
    def delete_file(user_uuid, relative_path):
        """
        Delete a file from storage.

        Args:
            user_uuid (str): User's UUID
            relative_path (str): Relative path to file

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = StorageService.get_full_path(user_uuid, relative_path)

            if not os.path.exists(full_path):
                return False, "File not found"

            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)

            return True, "File deleted successfully"

        except Exception as e:
            current_app.logger.error(f"File delete error: {str(e)}")
            return False, f"Failed to delete file: {str(e)}"

    @staticmethod
    def create_folder(user_uuid, relative_path):
        """
        Create a folder in storage.

        Args:
            user_uuid (str): User's UUID
            relative_path (str): Relative path for new folder

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = StorageService.get_full_path(user_uuid, relative_path)

            if os.path.exists(full_path):
                return False, "Folder already exists"

            if not ensure_directory_exists(full_path):
                return False, "Failed to create folder"

            return True, "Folder created successfully"

        except Exception as e:
            current_app.logger.error(f"Folder create error: {str(e)}")
            return False, f"Failed to create folder: {str(e)}"

    @staticmethod
    def move_file(user_uuid, old_relative_path, new_relative_path):
        """
        Move or rename a file.

        Args:
            user_uuid (str): User's UUID
            old_relative_path (str): Current relative path
            new_relative_path (str): New relative path

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            old_full_path = StorageService.get_full_path(user_uuid, old_relative_path)
            new_full_path = StorageService.get_full_path(user_uuid, new_relative_path)

            if not os.path.exists(old_full_path):
                return False, "Source file not found"

            if os.path.exists(new_full_path):
                return False, "Destination already exists"

            # Ensure destination directory exists
            new_directory = os.path.dirname(new_full_path)
            if not ensure_directory_exists(new_directory):
                return False, "Failed to create destination directory"

            # Move file
            shutil.move(old_full_path, new_full_path)

            return True, "File moved successfully"

        except Exception as e:
            current_app.logger.error(f"File move error: {str(e)}")
            return False, f"Failed to move file: {str(e)}"

    @staticmethod
    def file_exists(user_uuid, relative_path):
        """
        Check if a file exists in storage.

        Args:
            user_uuid (str): User's UUID
            relative_path (str): Relative path to file

        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = StorageService.get_full_path(user_uuid, relative_path)
        return os.path.exists(full_path)

    @staticmethod
    def get_file_size(user_uuid, relative_path):
        """
        Get the size of a file.

        Args:
            user_uuid (str): User's UUID
            relative_path (str): Relative path to file

        Returns:
            int: File size in bytes, or 0 if file doesn't exist
        """
        full_path = StorageService.get_full_path(user_uuid, relative_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return os.path.getsize(full_path)
        return 0
