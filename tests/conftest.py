"""
Pytest test fixtures and configuration for ALTO.
Sets up an isolated in-memory SQLite database and test clients.
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Transaction, Budget


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Creates and returns a registered test user."""
    with app.app_context():
        user = User(name='Test User', email='test@example.com', currency='₹')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        # Reload user to ensure detached state has valid ID
        user_id = user.id
        return db.session.get(User, user_id)


@pytest.fixture
def second_user(app):
    """Creates and returns a second registered test user for isolation tests."""
    with app.app_context():
        user = User(name='Second User', email='second@example.com', currency='$')
        user.set_password('password456')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return db.session.get(User, user_id)


def login(client, email='test@example.com', password='password123'):
    """Helper function to log in a test user."""
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


def logout(client):
    """Helper function to log out a test user."""
    return client.get('/logout', follow_redirects=True)
