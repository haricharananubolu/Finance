"""
End-to-end integration flow tests verifying CSRF, login, and full flow.
"""
import re
from app import create_app
from app.models import User, Transaction, Budget
from app.extensions import db


def test_csrf_and_full_user_flow(auth_user):
    """Test full flow with CSRF token extraction in development mode."""
    dev_app = create_app('development')
    client = dev_app.test_client()

    # 1. Landing Page
    r1 = client.get('/')
    assert r1.status_code == 200

    # 2. Extract CSRF token from Login page
    r2 = client.get('/login')
    assert r2.status_code == 200
    html = r2.data.decode('utf-8')
    match = re.search(r'name="csrf_token".*?value="([^"]+)"', html)
    assert match is not None
    token = match.group(1)

    # 3. Post login credentials with valid CSRF token
    r3 = client.post('/login', data={
        'email': 'demo@alto.app',
        'password': 'alto1234',
        'csrf_token': token
    }, follow_redirects=True)
    assert r3.status_code == 200
    assert b'Financial Overview' in r3.data

    # 4. View Transactions
    r4 = client.get('/transactions')
    assert r4.status_code == 200

    # 5. View Budgets
    r5 = client.get('/budgets')
    assert r5.status_code == 200

    # 6. View Reports
    r6 = client.get('/reports')
    assert r6.status_code == 200

    # 7. CSV Export
    r7 = client.get('/reports/export-csv')
    assert r7.status_code == 200
    assert 'text/csv' in r7.headers['Content-Type']

    # 8. View Profile
    r8 = client.get('/profile')
    assert r8.status_code == 200

    # 9. Logout
    r9 = client.get('/logout', follow_redirects=True)
    assert r9.status_code == 200
    assert b'logged out safely' in r9.data
