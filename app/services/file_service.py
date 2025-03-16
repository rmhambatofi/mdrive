from app import db
from app.models.file import File
from app.services.storage_service import StorageService


class FileService:
    @staticmethod
    def upload_file(file, user_id, parent_id=None):
        """
        Upload a file and save its metadata to the database
        
        Args:
            file: The file object from request.files
            user_id: The ID of the user uploading the file
            parent_id: Optional ID of the parent folder
            
        Returns:
            File: The created File object
        """
        # Get parent folder path if parent_id is provided
        parent_path = None
        if parent_id is None:
            # No parent folder, use root
            root_folder = FileService.get_user_root_folder(user_id)
            parent_id = root_folder.id
            parent_path = str(user_id)
        # Normal parent folder lookup if parent_id is provided
        elif parent_id:
            parent_file = File.query.get(parent_id)
            if parent_file and parent_file.mime_type == 'application/x-directory' and parent_file.owner_id == user_id:
                parent_path = parent_file.file_path
            else:
                # Parent folder doesn't exist, use user's root folder
                root_folder = FileService.get_user_root_folder(user_id)
                parent_id = root_folder.id
                parent_path = str(user_id)

        # Save the file to storage
        file_info = StorageService.save_file(file, user_id, parent_path)
        if not file_info:
            return None

        # Create file record in database
        new_file = File(
            name=file_info['original_filename'],
            storage_path=file_info['file_path'],
            size=file_info['file_size'],
            mime_type=file_info['file_type'],
            folder_id=parent_id,
            owner_id=user_id
        )

        db.session.add(new_file)
        db.session.commit()

        return new_file

    @staticmethod
    def create_folder(folder_name, user_id, parent_id=None):
        """
        Create a new folder and save its metadata to the database
        
        Args:
            folder_name: Name of the folder to create
            user_id: The ID of the user creating the folder
            parent_id: Optional ID of the parent folder
            
        Returns:
            File: The created folder object
        """
        # Get parent folder path if parent_id is provided
        parent_path = None
        parent_folder = None
        
        if parent_id is None:
            # No parent folder, use user's root folder
            parent_folder = FileService.get_user_root_folder(user_id)
            parent_id = parent_folder.id
            parent_path = str(user_id)
        # Normal parent folder lookup if parent_id is provided
        elif parent_id:
            from app.models.file import Folder
            parent_folder = Folder.query.filter_by(id=parent_id, owner_id=user_id).first()
            if parent_folder:
                parent_path = parent_folder.get_path().lstrip('/')
            else:
                # Parent folder doesn't exist, use user's root folder
                parent_folder = FileService.get_user_root_folder(user_id)
                parent_id = parent_folder.id
                parent_path = str(user_id)

        # Create the folder in storage
        folder_path = StorageService.create_folder(folder_name, user_id, parent_path)

        # Create folder record in database
        from app.models.file import File
        new_folder = File(
            name=folder_name,
            extension=None,
            mime_type='application/x-directory',
            size=0,
            storage_path=folder_path,
            folder_id=parent_id,
            owner_id=user_id,
            is_deleted=False
        )

        db.session.add(new_folder)
        db.session.commit()

        return new_folder

    @staticmethod
    def get_user_files(user_id, parent_id=None):
        """
        Get all files and folders for a user, optionally filtered by parent folder
        
        Args:
            user_id: The ID of the user
            parent_id: Optional ID of the parent folder
            
        Returns:
            list: List of File objects
        """
        query = File.query.filter_by(owner_id=user_id)

        if parent_id is not None:
            query = query.filter_by(folder_id=parent_id)
        else:
            # When no parent_id is specified, get files at the root level
            query = query.filter_by(folder_id=None)

        return query.all()

    @staticmethod
    def get_file_by_id(file_id, user_id):
        """
        Get a file by its ID, ensuring it belongs to the specified user
        
        Args:
            file_id: The ID of the file to retrieve
            user_id: The ID of the user who should own the file
            
        Returns:
            File: The file object if found and owned by the user, None otherwise
        """
        return File.query.filter_by(id=file_id, owner_id=user_id).first()

    @staticmethod
    def rename_file(file_id, new_name, user_id):
        """
        Rename a file or folder
        
        Args:
            file_id: The ID of the file to rename
            new_name: The new name for the file
            user_id: The ID of the user who owns the file
            
        Returns:
            File: The updated file object if successful, None otherwise
        """
        file = FileService.get_file_by_id(file_id, user_id)
        if not file:
            return None

        file.original_filename = new_name
        db.session.commit()

        return file

    @staticmethod
    def move_file(file_id, new_parent_id, user_id):
        """
        Move a file or folder to a different parent folder
        
        Args:
            file_id: The ID of the file to move
            new_parent_id: The ID of the new parent folder (None for root)
            user_id: The ID of the user who owns the file
            
        Returns:
            File: The updated file object if successful, None otherwise
        """
        file = FileService.get_file_by_id(file_id, user_id)
        if not file:
            return None

        # If moving to root
        if new_parent_id is None:
            file.parent_id = None
            db.session.commit()
            return file

        # Check if new parent exists and is a folder
        new_parent = FileService.get_file_by_id(new_parent_id, user_id)
        if not new_parent or not new_parent.is_folder:
            return None

        # Prevent moving a folder into itself or its descendants
        if file.is_folder:
            current = new_parent
            while current:
                if current.id == file.id:
                    return None
                current = current.parent

        file.parent_id = new_parent_id
        db.session.commit()

        return file

    @staticmethod
    def delete_file(file_id, user_id):
        """
        Delete a file or folder
        
        Args:
            file_id: The ID of the file to delete
            user_id: The ID of the user who owns the file
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        file = FileService.get_file_by_id(file_id, user_id)
        if not file:
            return False

        # Delete the file from storage
        if not StorageService.delete_file(file.file_path, user_id):
            return False

        # Delete the file record from database
        db.session.delete(file)
        db.session.commit()

        return True

    @staticmethod
    def search_files(query, user_id):
        """
        Search for files and folders by name
        
        Args:
            query: The search query string
            user_id: The ID of the user whose files to search
            
        Returns:
            list: List of matching File objects
        """
        return File.query.filter(
            File.user_id == user_id,
            File.original_filename.ilike(f'%{query}%')
        ).all()

    @staticmethod
    def find_folder(folder_name, user_id, parent_id=None):
        """
        Find a folder by name, optionally within a specific parent folder
        
        Args:
            folder_name: Name of the folder to find
            user_id: The ID of the user who owns the folder
            parent_id: Optional ID of the parent folder to search within
            
        Returns:
            File: The folder object if found, None otherwise
        """
        query = File.query.filter_by(
            user_id=user_id,
            is_folder=True,
            original_filename=folder_name
        )
        
        if parent_id is not None:
            query = query.filter_by(folder_id=parent_id)
            
        return query.first()
    
    @staticmethod
    def find_folder_by_path(folder_path, user_id):
        """
        Find a folder by its path
        
        Args:
            folder_path: Path of the folder to find (e.g., 'documents/projects')
            user_id: The ID of the user who owns the folder
            
        Returns:
            File: The folder object if found, None otherwise
        """
        if not folder_path:
            return None
            
        # Split the path into components
        path_components = folder_path.strip('/').split('/')
        
        # Start from root
        current_folder = None
        
        # Traverse the path
        for component in path_components:
            query = File.query.filter_by(
                user_id=user_id,
                is_folder=True,
                original_filename=component,
                parent_id=current_folder.id if current_folder else None
            )
            
            current_folder = query.first()
            if not current_folder:
                return None
                
    @staticmethod
    def get_user_root_folder(user_id):
        """
        Get the root folder for a user. If it doesn't exist, create it.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Folder: The user's root folder
        """
        from app.models.file import Folder
        
        # Try to find the user's root folder
        root_folder = Folder.query.filter_by(
            owner_id=user_id,
            parent_id=None,
            name=str(user_id)
        ).first()
        
        # If root folder doesn't exist, create it
        if not root_folder:
            root_folder = Folder(
                name=str(user_id),
                parent_id=None,
                owner_id=user_id
            )
            db.session.add(root_folder)
            db.session.commit()
            
            # Create the physical directory
            import os
            from flask import current_app
            user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
            os.makedirs(user_dir, exist_ok=True)
        
        return root_folder
        
        return current_folder
