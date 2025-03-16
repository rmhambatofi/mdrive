from app import create_app, db
from app.models.user import User
from app.models.file import File, Folder
import os

# Create a Flask application context
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def seed_database():
    """Seed the database with initial data"""
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(username='admin', email='admin@example.com')
            admin.password = 'adminpassword'  # This will be hashed by the setter
            db.session.add(admin)
            
            # Commit to generate the admin ID
            db.session.commit()
            
            # Create a root folder for admin
            root_folder = Folder(
                name='root',
                parent_id=None,
                owner_id=admin.id  # Use the actual admin ID
            )
            db.session.add(root_folder)
            
            db.session.commit()
            print('Database seeded successfully!')
        else:
            print('Admin user already exists, skipping seed.')

if __name__ == '__main__':
    seed_database()