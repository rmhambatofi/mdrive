"""
Authentication tests
Tests for user registration, login, and profile operations.
"""
import pytest
from app import create_app, db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestUserRegistration:
    """Test user registration functionality."""

    def test_successful_registration(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['full_name'] == 'Test User'

    def test_registration_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'password': 'Test123456',
            'full_name': 'Test User'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_registration_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'weak',
            'full_name': 'Test User'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_registration_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # First registration
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })

        # Duplicate registration
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Another User'
        })

        assert response.status_code == 409
        data = response.get_json()
        assert 'already registered' in data['error'].lower()


class TestUserLogin:
    """Test user login functionality."""

    def test_successful_login(self, client):
        """Test successful login."""
        # Register user first
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })

        # Login
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test123456'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'test@example.com'

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        # Register user first
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })

        # Login with wrong password
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'Test123456'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


class TestUserProfile:
    """Test user profile operations."""

    def test_get_profile(self, client):
        """Test getting user profile."""
        # Register user
        register_response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })
        token = register_response.get_json()['access_token']

        # Get profile
        response = client.get('/api/auth/profile',
                            headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'test@example.com'

    def test_get_profile_unauthorized(self, client):
        """Test getting profile without token."""
        response = client.get('/api/auth/profile')

        assert response.status_code == 401

    def test_update_profile(self, client):
        """Test updating user profile."""
        # Register user
        register_response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test123456',
            'full_name': 'Test User'
        })
        token = register_response.get_json()['access_token']

        # Update profile
        response = client.put('/api/auth/profile',
                            json={'full_name': 'Updated Name'},
                            headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['full_name'] == 'Updated Name'
