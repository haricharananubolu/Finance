"""
Unit and integration tests for authentication features in ALTO.
"""
from app.models import User
from tests.conftest import login, logout


def test_landing_page(client):
    """Test that public landing page loads properly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Take Control of' in response.data
    assert b'ALTO' in response.data


def test_registration_success(client, app):
    """Test user can register with valid credentials."""
    response = client.post('/register', data={
        'name': 'New Student',
        'email': 'student@example.com',
        'password': 'secretpassword',
        'password_confirm': 'secretpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'account has been created successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='student@example.com').first()
        assert user is not None
        assert user.name == 'New Student'
        assert user.check_password('secretpassword') is True
        assert user.check_password('wrongpassword') is False


def test_registration_duplicate_email(client, auth_user):
    """Test registering with an existing email returns an error message."""
    response = client.post('/register', data={
        'name': 'Duplicate User',
        'email': 'test@example.com',  # Already exists from auth_user fixture
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert b'already exists' in response.data


def test_registration_password_mismatch(client):
    """Test password confirmation mismatch produces validation error."""
    response = client.post('/register', data={
        'name': 'Mismatch User',
        'email': 'mismatch@example.com',
        'password': 'password123',
        'password_confirm': 'different456'
    }, follow_redirects=True)

    assert b'Passwords must match' in response.data


def test_login_success(client, auth_user):
    """Test registered user can log in."""
    response = login(client, 'test@example.com', 'password123')
    assert response.status_code == 200
    assert b'Welcome back' in response.data
    assert b'Financial Overview' in response.data


def test_login_invalid_password(client, auth_user):
    """Test wrong password rejects authentication."""
    response = login(client, 'test@example.com', 'wrongpassword')
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_login_nonexistent_user(client):
    """Test logging in with an unregistered email shows error."""
    response = login(client, 'nobody@example.com', 'anypassword')
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(client, auth_user):
    """Test user logout terminates session."""
    login(client, 'test@example.com', 'password123')
    response = logout(client)
    assert response.status_code == 200
    assert b'logged out safely' in response.data


def test_protected_routes_require_login(client):
    """Test unauthenticated access to protected routes redirects to login."""
    routes = ['/dashboard', '/transactions', '/transactions/new', '/budgets', '/budgets/new', '/reports', '/profile']
    for route in routes:
        response = client.get(route, follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in to access this page' in response.data
