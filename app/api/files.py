from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.file_service import FileService
import os

files = Blueprint('files', __name__)


@files.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file to the user's storage"""
    current_user_id = get_jwt_identity()
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Get parent folder ID if provided
    parent_id = request.form.get('parent_id')
    if parent_id:
        try:
            parent_id = int(parent_id)
        except ValueError:
            return jsonify({'message': 'Invalid parent ID'}), 400
    
    # Upload file
    new_file = FileService.upload_file(file, current_user_id, parent_id)
    if not new_file:
        return jsonify({'message': 'Error uploading file'}), 500
    
    return jsonify({
        'message': 'File uploaded successfully',
        'file': {
            'id': new_file.id,
            'filename': new_file.original_filename,
            'file_type': new_file.file_type,
            'file_size': new_file.file_size,
            'is_folder': new_file.is_folder,
            'parent_id': new_file.parent_id
        }
    }), 201


@files.route('/folder', methods=['POST'])
@jwt_required()
def create_folder():
    """Create a new folder"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('folder_name'):
        return jsonify({'message': 'Missing folder name'}), 400
    
    folder_name = data.get('folder_name')
    parent_id = data.get('parent_id')
    
    # Create folder
    new_folder = FileService.create_folder(folder_name, current_user_id, parent_id)
    if not new_folder:
        return jsonify({'message': 'Error creating folder'}), 500
    
    return jsonify({
        'message': 'Folder created successfully',
        'folder': {
            'id': new_folder.id,
            'filename': new_folder.original_filename,
            'is_folder': new_folder.is_folder,
            'parent_id': new_folder.parent_id
        }
    }), 201


@files.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    """List files and folders for the current user"""
    current_user_id = get_jwt_identity()
    
    # Get parent folder ID if provided
    parent_id = request.args.get('parent_id')
    if parent_id:
        try:
            parent_id = int(parent_id)
        except ValueError:
            return jsonify({'message': 'Invalid parent ID'}), 400
    
    # Get files and folders
    files_list = FileService.get_user_files(current_user_id, parent_id)
    
    # Format response
    result = []
    for file in files_list:
        result.append({
            'id': file.id,
            'filename': file.original_filename,
            'file_type': file.file_type,
            'file_size': file.file_size,
            'is_folder': file.is_folder,
            'parent_id': file.parent_id,
            'created_at': file.created_at.isoformat() if file.created_at else None
        })
    
    return jsonify({
        'files': result
    }), 200


@files.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Download a file"""
    current_user_id = get_jwt_identity()
    
    # Get file
    file = FileService.get_file_by_id(file_id, current_user_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Cannot download folders
    if file.is_folder:
        return jsonify({'message': 'Cannot download a folder'}), 400
    
    # Return file
    return send_file(
        file.file_path,
        download_name=file.original_filename,
        as_attachment=True
    )


@files.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a file or folder"""
    current_user_id = get_jwt_identity()
    
    # Delete file
    result = FileService.delete_file(file_id, current_user_id)
    if not result:
        return jsonify({'message': 'Error deleting file'}), 500
    
    return jsonify({'message': 'File deleted successfully'}), 200


@files.route('/<int:file_id>/rename', methods=['PUT'])
@jwt_required()
def rename_file(file_id):
    """Rename a file or folder"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('new_name'):
        return jsonify({'message': 'Missing new name'}), 400
    
    new_name = data.get('new_name')
    
    # Rename file
    updated_file = FileService.rename_file(file_id, new_name, current_user_id)
    if not updated_file:
        return jsonify({'message': 'Error renaming file'}), 500
    
    return jsonify({
        'message': 'File renamed successfully',
        'file': {
            'id': updated_file.id,
            'filename': updated_file.original_filename
        }
    }), 200


@files.route('/<int:file_id>/move', methods=['PUT'])
@jwt_required()
def move_file(file_id):
    """Move a file or folder to a different parent folder"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # New parent ID can be null (for root)
    new_parent_id = data.get('new_parent_id')
    if new_parent_id is not None:
        try:
            new_parent_id = int(new_parent_id)
        except ValueError:
            return jsonify({'message': 'Invalid parent ID'}), 400
    
    # Move file
    updated_file = FileService.move_file(file_id, new_parent_id, current_user_id)
    if not updated_file:
        return jsonify({'message': 'Error moving file'}), 500
    
    return jsonify({
        'message': 'File moved successfully',
        'file': {
            'id': updated_file.id,
            'parent_id': updated_file.parent_id
        }
    }), 200