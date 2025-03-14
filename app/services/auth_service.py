from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token


class AuthService:
    @staticmethod
    def register_user(username, email, password):
        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None

        # Create new user
        user = User(username=username, email=email)
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
    def create_user(username, password, email=None):
        # Create new user
        user = User(username=username, email=email)
        user.password = password

        db.session.add(user)
        db.session.commit()

        return user
        
    @staticmethod
    def authenticate_user(username, password):
        user = AuthService.get_user_by_username(username)
        if user and user.verify_password(password):
            return user
        return None
