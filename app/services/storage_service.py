import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class StorageService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def save_file(file, user_id, parent_folder=None):
        """
        Save a file to the storage system
        
        Args:
            file: The file object from request.files
            user_id: The ID of the user uploading the file
            parent_folder: Optional parent folder path
            
        Returns:
            dict: Information about the saved file
        """
        if not file or not StorageService.allowed_file(file.filename):
            return None
        
        # Generate a secure filename with UUID to prevent collisions
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Determine the full path where the file will be saved
        if parent_folder:
            folder_path = os.path.join(user_dir, parent_folder)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, filename)
            relative_path = os.path.join(parent_folder, filename)
        else:
            file_path = os.path.join(user_dir, filename)
            relative_path = filename
        
        # Save the file
        file.save(file_path)
        
        # Get file size and type
        file_size = os.path.getsize(file_path)
        file_type = file.content_type if hasattr(file, 'content_type') else None
        
        return {
            'filename': filename,
            'original_filename': original_filename,
            'file_path': relative_path,
            'file_size': file_size,
            'file_type': file_type
        }
    
    @staticmethod
    def create_folder(folder_name, user_id, parent_folder=None):
        """
        Create a new folder in the storage system
        
        Args:
            folder_name: Name of the folder to create
            user_id: The ID of the user creating the folder
            parent_folder: Optional parent folder path
            
        Returns:
            str: Path to the created folder
        """
        # Secure the folder name
        folder_name = secure_filename(folder_name)
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Determine the full path where the folder will be created
        if parent_folder:
            parent_path = os.path.join(user_dir, parent_folder)
            folder_path = os.path.join(parent_path, folder_name)
            relative_path = os.path.join(parent_folder, folder_name)
        else:
            folder_path = os.path.join(user_dir, folder_name)
            relative_path = folder_name
        
        # Create the folder
        os.makedirs(folder_path, exist_ok=True)
        
        return relative_path
    
    @staticmethod
    def delete_file(file_path, user_id):
        """
        Delete a file from the storage system
        
        Args:
            file_path: Path to the file relative to the user's directory
            user_id: The ID of the user who owns the file
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id), file_path)
        
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                import shutil
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return True
        
        return False