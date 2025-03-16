from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.files import files
from app.models.file import Folder, File
from app.services.file_service import FileService


@files.route('/folder', methods=['POST'])
@jwt_required()
def create_folder():
    """Create a new folder"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({'message': 'Missing folder name'}), 400

    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    if any(char in folder_name for char in invalid_chars):
        return jsonify({'error': 'The folder name contains unauthorized characters'}), 400

    parent_id = data.get('parent_id')
    
    # Create folder - the FileService will handle parent folder validation
    # and will use the user's root folder if parent_id is None or invalid
    new_folder = FileService.create_folder(folder_name, current_user_id, parent_id)
    if not new_folder:
        return jsonify({'message': 'Error creating folder'}), 500
    
    return jsonify({
        'message': 'Folder created successfully',
        'folder': {
            'id': new_folder.id,
            'filename': new_folder.name,
            'is_folder': True,
            'parent_id': new_folder.folder_id
        }
    }), 201


@files.route('/folder/<int:folder_id>', methods=['GET'])
@jwt_required()
def get_folder_details(folder_id):
    """Get folder details and contents"""
    user_id = get_jwt_identity()
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

    folder = Folder.query.filter_by(id=folder_id, owner_id=user_id).first()

    if not folder:
        return jsonify({'error': 'Dossier non trouvé'}), 404

    # Récupérer les sous-dossiers
    subfolders_query = Folder.query.filter_by(parent_id=folder_id)
    if not include_deleted:
        subfolders_query = subfolders_query.filter_by(is_deleted=False)
    subfolders = subfolders_query.all()

    # Récupérer les fichiers dans ce dossier
    files_query = File.query.filter_by(folder_id=folder_id)
    if not include_deleted:
        files_query = files_query.filter_by(is_deleted=False)
    files = files_query.all()

    folder_data = {
        'id': folder.id,
        'name': folder.name,
        'parent_id': folder.parent_id,
        'created_at': folder.created_at.isoformat(),
        'updated_at': folder.updated_at.isoformat(),
        'is_deleted': folder.is_deleted,
        'path': folder.get_path(),
        'size': folder.get_size(),
        'subfolders': [{
            'id': subfolder.id,
            'name': subfolder.name,
            'created_at': subfolder.created_at.isoformat(),
            'updated_at': subfolder.updated_at.isoformat(),
            'is_deleted': subfolder.is_deleted
        } for subfolder in subfolders],
        'files': [{
            'id': file.id,
            'name': file.name,
            'extension': file.extension,
            'size': file.size,
            'mime_type': file.mime_type,
            'created_at': file.created_at.isoformat(),
            'updated_at': file.updated_at.isoformat(),
            'is_deleted': file.is_deleted,
            'is_favorite': file.is_favorite
        } for file in files]
    }

    return jsonify(folder_data), 200


@files.route('/folder/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    """Delete a folder and all its contents"""
    current_user_id = get_jwt_identity()
    
    # Verify folder exists and belongs to the user
    folder = Folder.query.filter_by(id=folder_id, owner_id=current_user_id).first()
    if not folder:
        return jsonify({'error': 'Folder not found'}), 404
    
    # Delete the folder and all its contents
    # The FileService will handle recursive deletion of subfolders and files
    result = FileService.delete_file(folder_id, current_user_id)
    if not result:
        return jsonify({'error': 'Error deleting folder'}), 500
    
    return jsonify({'message': 'Folder deleted successfully'}), 200


@files.route('/folder/default', methods=['GET'])
@jwt_required()
def get_default_folder():
    """Get the current user's default root folder details"""
    user_id = get_jwt_identity()
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
    # Get the user's root folder
    folder = FileService.get_user_root_folder(user_id)
    
    if not folder:
        return jsonify({'error': 'Default folder not found'}), 404
    
    # Retrieve subfolders
    subfolders_query = Folder.query.filter_by(parent_id=folder.id)
    if not include_deleted:
        subfolders_query = subfolders_query.filter_by(is_deleted=False)
    subfolders = subfolders_query.all()
    
    # Retrieve files in this folder
    files_query = File.query.filter_by(folder_id=folder.id)
    if not include_deleted:
        files_query = files_query.filter_by(is_deleted=False)
    files = files_query.all()
    
    folder_data = {
        'id': folder.id,
        'name': folder.name,
        'parent_id': folder.parent_id,
        'created_at': folder.created_at.isoformat(),
        'updated_at': folder.updated_at.isoformat(),
        'is_deleted': folder.is_deleted,
        'path': folder.get_path(),
        'size': folder.get_size(),
        'subfolders': [{
            'id': subfolder.id,
            'name': subfolder.name,
            'created_at': subfolder.created_at.isoformat(),
            'updated_at': subfolder.updated_at.isoformat(),
            'is_deleted': subfolder.is_deleted
        } for subfolder in subfolders],
        'files': [{
            'id': file.id,
            'name': file.name,
            'extension': file.extension,
            'size': file.size,
            'mime_type': file.mime_type,
            'created_at': file.created_at.isoformat(),
            'updated_at': file.updated_at.isoformat(),
            'is_deleted': file.is_deleted,
            'is_favorite': file.is_favorite
        } for file in files]
    }
    
    return jsonify(folder_data), 200

    