"""
Database initialization script.
Creates all tables and optionally creates a test user.
"""
import os
from app import create_app, db
from app.models.user import User
from app.models.file import File

def init_database():
    """Initialize the database with tables."""
    print("Initializing database...")

    # Create Flask app
    app = create_app('development')

    with app.app_context():
        # Drop all tables (optional - comment out in production)
        print("Dropping existing tables...")
        db.drop_all()

        # Create all tables
        print("Creating tables...")
        db.create_all()

        print("Database tables created successfully!")

        # Create test user (optional)
        create_test = input("\nDo you want to create a test user? (y/n): ").lower()
        if create_test == 'y':
            email = input("Enter email: ")
            password = input("Enter password: ")
            full_name = input("Enter full name: ")

            try:
                user = User(
                    email=email,
                    password=password,
                    full_name=full_name
                )
                db.session.add(user)
                db.session.commit()

                # Create user directory
                user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user.uuid)
                os.makedirs(user_dir, exist_ok=True)

                print(f"\nTest user created successfully!")
                print(f"Email: {user.email}")
                print(f"UUID: {user.uuid}")
                print(f"Storage directory: {user_dir}")

            except Exception as e:
                print(f"\nError creating test user: {str(e)}")
                db.session.rollback()

        print("\nDatabase initialization complete!")


if __name__ == '__main__':
    init_database()
