"""
File controller module.
Handles HTTP requests for file operations.
"""
import os
from flask import request, jsonify, send_file, current_app
from datetime import datetime
from werkzeug.utils import safe_join
from app.services.file_service import FileService
from app.services.storage_service import StorageService
from app.middleware.auth_middleware import jwt_required_custom


class FileController:
    """Controller for file management endpoints."""

    @staticmethod
    @jwt_required_custom
    def upload_file(user):
        """
        Handle file upload request.

        Requires: JWT token in Authorization header
        Expected form data:
            - file: File object
            - parent_folder_id: (optional) Parent folder UUID

        Returns:
            JSON response with uploaded file data
        """
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Get parent folder UUID (optional)
            parent_folder_uuid = request.form.get('parent_folder_id')

            # Upload file
            success, response_data, status_code = FileService.upload_file(
                user=user,
                file_object=file,
                parent_folder_uuid=parent_folder_uuid
            )

            return jsonify(response_data), status_code

        except Exception as e:
            current_app.logger.error(f"Upload endpoint error: {str(e)}")
            return jsonify({'error': 'Upload failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def get_files(user):
        """
        Get list of files and folders.

        Requires: JWT token in Authorization header
        Query parameters:
            - folder_id: (optional) Parent folder UUID
            - page: (optional) Page number (default: 1)
            - per_page: (optional) Items per page (default: 50)

        Returns:
            JSON response with files list and pagination
        """
        try:
            folder_uuid = request.args.get('folder_id')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)

            # Validate pagination
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 50

            success, response_data, status_code = FileService.get_files(
                user=user,
                parent_folder_uuid=folder_uuid,
                page=page,
                per_page=per_page
            )

            return jsonify(response_data), status_code

        except Exception as e:
            current_app.logger.error(f"Get files endpoint error: {str(e)}")
            return jsonify({'error': 'Failed to retrieve files', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def download_file(user, file_uuid):
        """
        Download a file.

        Requires: JWT token in Authorization header
        URL parameter:
            - file_uuid: File UUID to download

        Returns:
            File stream with appropriate headers
        """
        try:
            # Get file from database
            success, file_data, status_code = FileService.get_file_by_uuid(user, file_uuid)

            if not success:
                return jsonify(file_data), status_code

            file_obj = file_data

            # Check if it's a folder
            if file_obj.is_folder:
                return jsonify({'error': 'Cannot download a folder'}), 400

            # Get full file path
            full_path = StorageService.get_full_path(user.uuid, file_obj.file_path)

            # Check if file exists
            if not os.path.exists(full_path):
                return jsonify({'error': 'File not found on storage'}), 404

            # Send file
            return send_file(
                full_path,
                as_attachment=True,
                download_name=file_obj.file_name,
                mimetype=file_obj.mime_type
            )

        except Exception as e:
            current_app.logger.error(f"Download endpoint error: {str(e)}")
            return jsonify({'error': 'Download failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def delete_file(user, file_uuid):
        """
        Delete a file or folder.

        Requires: JWT token in Authorization header
        URL parameter:
            - file_uuid: File UUID to delete

        Returns:
            JSON response confirming deletion
        """
        try:
            success, response_data, status_code = FileService.delete_file(
                user=user,
                file_uuid=file_uuid
            )

            return jsonify(response_data), status_code

        except Exception as e:
            current_app.logger.error(f"Delete endpoint error: {str(e)}")
            return jsonify({'error': 'Delete failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def create_folder(user):
        """
        Create a new folder.

        Requires: JWT token in Authorization header
        Expected JSON body:
            {
                "folder_name": "New Folder",
                "parent_folder_id": (optional) "uuid-string"
            }

        Returns:
            JSON response with created folder data
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            folder_name = data.get('folder_name')
            parent_folder_uuid = data.get('parent_folder_id')

            if not folder_name:
                return jsonify({'error': 'Folder name is required'}), 400

            success, response_data, status_code = FileService.create_folder(
                user=user,
                folder_name=folder_name,
                parent_folder_uuid=parent_folder_uuid
            )

            return jsonify(response_data), status_code

        except Exception as e:
            current_app.logger.error(f"Create folder endpoint error: {str(e)}")
            return jsonify({'error': 'Folder creation failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def rename_file(user, file_uuid):
        """
        Rename a file or folder.

        Requires: JWT token in Authorization header
        URL parameter:
            - file_uuid: File UUID to rename
        Expected JSON body:
            {
                "new_name": "New File Name.pdf"
            }

        Returns:
            JSON response with updated file data
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            new_name = data.get('new_name')

            if not new_name:
                return jsonify({'error': 'New name is required'}), 400

            success, response_data, status_code = FileService.rename_file(
                user=user,
                file_uuid=file_uuid,
                new_name=new_name
            )

            return jsonify(response_data), status_code

        except Exception as e:
            current_app.logger.error(f"Rename endpoint error: {str(e)}")
            return jsonify({'error': 'Rename failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def download_zip(user):
        """
        Create and download a ZIP archive of the specified files/folders.

        Requires: JWT token in Authorization header
        Expected JSON body:
            {
                "file_ids": ["uuid1", "uuid2", ...]
            }

        Returns:
            ZIP file stream
        """
        try:
            data = request.get_json()

            if not data or not data.get('file_ids'):
                return jsonify({'error': 'No file IDs provided'}), 400

            file_uuids = data['file_ids']

            if not isinstance(file_uuids, list) or len(file_uuids) == 0:
                return jsonify({'error': 'file_ids must be a non-empty list'}), 400

            success, result, status_code = FileService.create_zip(user, file_uuids)

            if not success:
                return jsonify(result), status_code

            zip_name = f"mdrive-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"

            return send_file(
                result,
                mimetype='application/zip',
                as_attachment=True,
                download_name=zip_name
            )

        except Exception as e:
            current_app.logger.error(f"Download ZIP endpoint error: {str(e)}")
            return jsonify({'error': 'ZIP download failed', 'details': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def get_file_info(user, file_uuid):
        """
        Get file/folder information.

        Requires: JWT token in Authorization header
        URL parameter:
            - file_uuid: File UUID

        Returns:
            JSON response with file data
        """
        try:
            success, file_data, status_code = FileService.get_file_by_uuid(user, file_uuid)

            if not success:
                return jsonify(file_data), status_code

            file_obj = file_data
            response = {
                'file': file_obj.to_dict(),
                'breadcrumb': file_obj.get_breadcrumb()
            }

            return jsonify(response), 200

        except Exception as e:
            current_app.logger.error(f"Get file info endpoint error: {str(e)}")
            return jsonify({'error': 'Failed to retrieve file info', 'details': str(e)}), 500
