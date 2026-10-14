"""
Unit and integration tests for transactions and financial data isolation in ALTO.
"""
from datetime import date
from decimal import Decimal
from app.models import Transaction
from app.extensions import db
from tests.conftest import login


def test_create_income_transaction(client, auth_user, app):
    """Test user can add an income transaction."""
    login(client, 'test@example.com', 'password123')

    response = client.post('/transactions/new', data={
        'transaction_type': 'income',
        'amount': '45000.00',
        'category': 'Salary',
        'description': 'Monthly salary paycheck',
        'payment_method': 'Net Banking',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Successfully added Income' in response.data

    with app.app_context():
        tx = Transaction.query.filter_by(user_id=auth_user.id).first()
        assert tx is not None
        assert tx.transaction_type == 'income'
        assert tx.amount == Decimal('45000.00')
        assert tx.category == 'Salary'


def test_create_expense_transaction(client, auth_user, app):
    """Test user can add an expense transaction."""
    login(client, 'test@example.com', 'password123')

    response = client.post('/transactions/new', data={
        'transaction_type': 'expense',
        'amount': '3200.50',
        'category': 'Groceries & Food',
        'description': 'Supermarket run',
        'payment_method': 'UPI / Instant Pay',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Successfully added Expense' in response.data

    with app.app_context():
        tx = Transaction.query.filter_by(user_id=auth_user.id, transaction_type='expense').first()
        assert tx is not None
        assert tx.amount == Decimal('3200.50')


def test_edit_transaction(client, auth_user, app):
    """Test updating an existing transaction."""
    with app.app_context():
        tx = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('500.00'),
            category='Dining Out & Cafes',
            description='Coffee with friend',
            payment_method='Cash',
            transaction_date=date.today()
        )
        db.session.add(tx)
        db.session.commit()
        tx_id = tx.id

    login(client, 'test@example.com', 'password123')

    response = client.post(f'/transactions/{tx_id}/edit', data={
        'transaction_type': 'expense',
        'amount': '750.00',
        'category': 'Dining Out & Cafes',
        'description': 'Dinner with friend',
        'payment_method': 'Cash',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Transaction updated successfully' in response.data

    with app.app_context():
        updated_tx = db.session.get(Transaction, tx_id)
        assert updated_tx.amount == Decimal('750.00')
        assert updated_tx.description == 'Dinner with friend'


def test_delete_transaction(client, auth_user, app):
    """Test deleting a transaction."""
    with app.app_context():
        tx = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('100.00'),
            category='Utilities & Bills',
            transaction_date=date.today()
        )
        db.session.add(tx)
        db.session.commit()
        tx_id = tx.id

    login(client, 'test@example.com', 'password123')

    response = client.post(f'/transactions/{tx_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Transaction has been deleted' in response.data

    with app.app_context():
        assert db.session.get(Transaction, tx_id) is None


def test_user_transaction_isolation(client, auth_user, second_user, app):
    """CRITICAL SECURITY TEST: Verify user B cannot view, edit, or delete user A's transaction."""
    with app.app_context():
        tx_user1 = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('9999.00'),
            category='Housing & Rent',
            description='Private Rent Payment',
            transaction_date=date.today()
        )
        db.session.add(tx_user1)
        db.session.commit()
        target_id = tx_user1.id

    # Log in as second user
    login(client, 'second@example.com', 'password456')

    # 1. User 2 views transactions list - User 1's record must not appear
    list_resp = client.get('/transactions')
    assert b'Private Rent Payment' not in list_resp.data

    # 2. User 2 tries to access edit page for User 1's transaction - MUST return 404
    edit_resp = client.get(f'/transactions/{target_id}/edit')
    assert edit_resp.status_code == 404

    # 3. User 2 tries to submit update to User 1's transaction - MUST return 404
    edit_post_resp = client.post(f'/transactions/{target_id}/edit', data={
        'transaction_type': 'expense',
        'amount': '1.00',
        'category': 'Housing & Rent',
        'payment_method': 'Cash',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    })
    assert edit_post_resp.status_code == 404

    # 4. User 2 tries to delete User 1's transaction - MUST return 404
    del_resp = client.post(f'/transactions/{target_id}/delete')
    assert del_resp.status_code == 404

    # Verify User 1's transaction is completely intact
    with app.app_context():
        intact_tx = db.session.get(Transaction, target_id)
        assert intact_tx is not None
        assert intact_tx.amount == Decimal('9999.00')


def test_invalid_transaction_amount(client, auth_user):
    """Test negative or zero amounts are rejected by validation."""
    login(client, 'test@example.com', 'password123')

    # Zero amount
    resp = client.post('/transactions/new', data={
        'transaction_type': 'income',
        'amount': '0.00',
        'category': 'Salary',
        'payment_method': 'Cash',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert b'Amount must be greater than 0.00' in resp.data

    # Negative amount
    resp2 = client.post('/transactions/new', data={
        'transaction_type': 'expense',
        'amount': '-50.00',
        'category': 'Groceries & Food',
        'payment_method': 'Cash',
        'transaction_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert b'Amount must be greater than 0.00' in resp2.data
