from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.files import files
from app.models.file import FileVersion
from app.services.file_service import FileService


@files.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file to the user's storage"""
    user_id = get_jwt_identity()
    
    # Vérifier si un fichier est présent dans la requête
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    # Vérifier si un fichier a été sélectionné
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    # Vérifier si l'extension est autorisée
    if not allowed_file(file.filename):
        return jsonify({'error': 'Type de fichier non autorisé'}), 400
    
    # Récupérer l'utilisateur
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Obtenir la taille du fichier
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    # Vérifier si l'utilisateur a assez d'espace de stockage
    if not user.has_storage_space(file_size):
        return jsonify({'error': 'Espace de stockage insuffisant'}), 400
    
    # Traiter les informations du fichier
    folder_id = request.form.get('folder_id')
    secure_name = secure_filename(file.filename)
    
    # Vérifier si le dossier existe
    if folder_id:
        folder = Folder.query.filter_by(id=folder_id, owner_id=user_id).first()
        if not folder:
            return jsonify({'error': 'Dossier non trouvé'}), 404
    
    # Vérifier si un fichier avec le même nom existe déjà dans ce dossier
    existing_file = File.query.filter_by(
        name=secure_name,
        folder_id=folder_id,
        owner_id=user_id,
        is_deleted=False
    ).first()
    
    # Si le fichier existe déjà, créer une nouvelle version
    if existing_file:
        # Déterminer le numéro de version
        latest_version = FileVersion.query.filter_by(file_id=existing_file.id).order_by(
            FileVersion.version_number.desc()
        ).first()
        
        version_number = (latest_version.version_number + 1) if latest_version else 2
        
        # Obtenir un chemin de stockage sécurisé pour la nouvelle version
        version_storage_path = get_secure_storage_path(user_id, secure_name)
        
        # Sauvegarder la version actuelle comme une version
        current_version = FileVersion(
            file_id=existing_file.id,
            version_number=1 if not latest_version else latest_version.version_number,
            size=existing_file.size,
            checksum=existing_file.checksum,
            storage_path=existing_file.storage_path,
            created_by=user_id,
            comment=request.form.get('comment', f'Version {version_number}')
        )
        
        db.session.add(current_version)
        
        # Mettre à jour le fichier existant avec les nouvelles informations
        success, error_msg = save_file(file, version_storage_path)
        if not success:
            return jsonify({'error': error_msg}), 500
        
        # Calculer le checksum
        checksum = generate_checksum(os.path.join(current_app.config['UPLOAD_FOLDER'], version_storage_path))
        
        # Mettre à jour le fichier principal
        existing_file.size = file_size
        existing_file.checksum = checksum
        existing_file.storage_path = version_storage_path
        existing_file.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': existing_file.id,
            'name': existing_file.name,
            'size': existing_file.size,
            'version': version_number,
            'folder_id': existing_file.folder_id,
            'updated_at': existing_file.updated_at.isoformat(),
            'message': 'Nouvelle version téléchargée avec succès'
        }), 200
    else:
        # Nouveau fichier
        extension = get_file_extension(file.filename)
        mime_type = get_file_mime_type(file)
        file.seek(0)
        
        # Obtenir un chemin de stockage sécurisé
        storage_path = get_secure_storage_path(user_id, secure_name)
        
        # Sauvegarder le fichier
        success, error_msg = save_file(file, storage_path)
        if not success:
            return jsonify({'error': error_msg}), 500
        
        # Calculer le checksum
        checksum = generate_checksum(os.path.join(current_app.config['UPLOAD_FOLDER'], storage_path))
        
        # Créer l'entrée du fichier dans la base de données
        new_file = File(
            name=secure_name,
            extension=extension,
            mime_type=mime_type,
            size=file_size,
            checksum=checksum,
            storage_path=storage_path,
            folder_id=folder_id,
            owner_id=user_id
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'id': new_file.id,
            'name': new_file.name,
            'extension': new_file.extension,
            'size': new_file.size,
            'folder_id': new_file.folder_id,
            'created_at': new_file.created_at.isoformat(),
            'message': 'Fichier téléchargé avec succès'
        }), 201


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
    if file.mime_type == 'application/x-directory':
        return jsonify({'message': 'Cannot download a folder'}), 400
    
    # Return file
    return send_file(
        file.get_physical_path(),
        download_name=file.name,
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
            'filename': updated_file.name
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
            'parent_id': updated_file.folder_id
        }
    }), 200


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
            'filename': file.name,
            'file_type': file.mime_type,
            'file_size': file.size,
            'is_folder': file.mime_type == 'application/x-directory',
            'parent_id': file.folder_id,
            'created_at': file.created_at.isoformat() if file.created_at else None
        })
    
    return jsonify({
        'files': result
    }), 200