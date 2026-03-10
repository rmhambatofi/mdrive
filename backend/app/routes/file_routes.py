"""
File routes module.
Defines URL endpoints for file operations.
"""
from flask import Blueprint
from app.controllers.file_controller import FileController

# Create blueprint
file_bp = Blueprint('files', __name__)


# Route definitions
@file_bp.route('/upload', methods=['POST'])
def upload_file():
    """POST /api/files/upload - Upload a file"""
    return FileController.upload_file()


@file_bp.route('', methods=['GET'])
def get_files():
    """GET /api/files - Get list of files and folders"""
    return FileController.get_files()


@file_bp.route('/<string:file_uuid>', methods=['GET'])
def get_file_info(file_uuid):
    """GET /api/files/<file_uuid> - Get file information"""
    return FileController.get_file_info(file_uuid)


@file_bp.route('/download/<string:file_uuid>', methods=['GET'])
def download_file(file_uuid):
    """GET /api/files/download/<file_uuid> - Download a file"""
    return FileController.download_file(file_uuid)


@file_bp.route('/download-zip', methods=['POST'])
def download_zip():
    """POST /api/files/download-zip - Download multiple files/folders as a ZIP"""
    return FileController.download_zip()


@file_bp.route('/<string:file_uuid>', methods=['DELETE'])
def delete_file(file_uuid):
    """DELETE /api/files/<file_uuid> - Delete a file or folder"""
    return FileController.delete_file(file_uuid)


@file_bp.route('/folder', methods=['POST'])
def create_folder():
    """POST /api/files/folder - Create a new folder"""
    return FileController.create_folder()


@file_bp.route('/<string:file_uuid>/rename', methods=['PUT'])
def rename_file(file_uuid):
    """PUT /api/files/<file_uuid>/rename - Rename a file or folder"""
    return FileController.rename_file(file_uuid)
