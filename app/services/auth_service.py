from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token
import os
from flask import current_app


class AuthService:
    @staticmethod
    def register_user(username, email, password, firstname=None, lastname=None):
        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None

        # Create new user
        user = User(username=username, email=email, firstname=firstname, lastname=lastname)
        user.password = password

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        return None
        
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
        
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
        
    @staticmethod
    def create_user(username, password, email=None, firstname=None, lastname=None):
        # Create new user
        user = User(username=username, email=email, firstname=firstname, lastname=lastname)
        user.password = password

        db.session.add(user)
        db.session.commit()
        
        # Create a user-specific root directory
        from app.models.file import Folder
        root_folder = Folder(
            name=str(user.id),  # Use user's technical ID as the root folder name
            parent_id=None,
            owner_id=user.id
        )
        db.session.add(root_folder)
        db.session.commit()
        
        # Create the physical directory
        import os
        from flask import current_app
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        return user
        
    @staticmethod
    def authenticate_user(username, password):
        user = AuthService.get_user_by_username(username)
        if user and user.verify_password(password):
            return user
        return None
        
    @staticmethod
    def delete_user(user_id):
        """Delete a user and all associated data
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # Get the user
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return False
            
        try:
            # Import here to avoid circular imports
            from app.models.file import File, Folder
            from app.services.file_service import FileService
            from app.services.storage_service import StorageService
            
            # Get all files and folders owned by the user
            files = File.query.filter_by(owner_id=user_id).all()
            folders = Folder.query.filter_by(owner_id=user_id).all()
            
            # Delete all files from storage and database
            for file in files:
                if not file.is_deleted:
                    # Delete the file from storage
                    StorageService.delete_file(file.storage_path, user_id)
                    # Delete the file from database
                    db.session.delete(file)
            
            # Delete all folders from database
            for folder in folders:
                db.session.delete(folder)
                
            # Delete the user's storage directory
            user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
            if os.path.exists(user_dir):
                import shutil
                shutil.rmtree(user_dir)
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user: {str(e)}")
            return False
