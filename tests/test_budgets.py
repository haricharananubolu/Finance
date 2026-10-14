"""
Unit and integration tests for budgets, progress calculations, and alert thresholds in ALTO.
"""
from datetime import date
from decimal import Decimal
from app.models import Budget, Transaction
from app.extensions import db
from tests.conftest import login


def test_create_budget(client, auth_user, app):
    """Test user can create a monthly budget."""
    login(client, 'test@example.com', 'password123')
    today = date.today()

    response = client.post('/budgets/new', data={
        'category': 'Groceries & Food',
        'monthly_limit': '8000.00',
        'month': str(today.month),
        'year': str(today.year)
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'created' in response.data

    with app.app_context():
        budget = Budget.query.filter_by(
            user_id=auth_user.id,
            category='Groceries & Food',
            month=today.month,
            year=today.year
        ).first()
        assert budget is not None
        assert budget.monthly_limit == Decimal('8000.00')


def test_budget_calculations_and_status(app, auth_user):
    """Test spent calculation and health status thresholds (healthy, warning, exceeded)."""
    today = date.today()

    with app.app_context():
        # 1. Budget of 1000.00
        budget = Budget(
            user_id=auth_user.id,
            category='Dining Out & Cafes',
            monthly_limit=Decimal('1000.00'),
            month=today.month,
            year=today.year
        )
        db.session.add(budget)
        db.session.commit()

        # Healthy state: spent 500 (50%)
        t1 = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('500.00'),
            category='Dining Out & Cafes',
            transaction_date=today
        )
        db.session.add(t1)
        db.session.commit()

        metrics = budget.calculate_spent_and_remaining()
        assert metrics['spent'] == 500.0
        assert metrics['remaining'] == 500.0
        assert metrics['status'] == 'healthy'

        # Warning state: add 350 -> total 850 (85%)
        t2 = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('350.00'),
            category='Dining Out & Cafes',
            transaction_date=today
        )
        db.session.add(t2)
        db.session.commit()

        metrics_warn = budget.calculate_spent_and_remaining()
        assert metrics_warn['spent'] == 850.0
        assert metrics_warn['remaining'] == 150.0
        assert metrics_warn['status'] == 'warning'

        # Exceeded state: add 200 -> total 1050 (105%)
        t3 = Transaction(
            user_id=auth_user.id,
            transaction_type='expense',
            amount=Decimal('200.00'),
            category='Dining Out & Cafes',
            transaction_date=today
        )
        db.session.add(t3)
        db.session.commit()

        metrics_exceeded = budget.calculate_spent_and_remaining()
        assert metrics_exceeded['spent'] == 1050.0
        assert metrics_exceeded['remaining'] == -50.0
        assert metrics_exceeded['status'] == 'exceeded'


def test_user_budget_isolation(client, auth_user, second_user, app):
    """Test user B cannot edit or delete user A's budget."""
    today = date.today()
    with app.app_context():
        b_user1 = Budget(
            user_id=auth_user.id,
            category='Entertainment & Subscriptions',
            monthly_limit=Decimal('2500.00'),
            month=today.month,
            year=today.year
        )
        db.session.add(b_user1)
        db.session.commit()
        b_id = b_user1.id

    # Log in as user 2
    login(client, 'second@example.com', 'password456')

    # Try to edit User 1's budget -> 404
    resp_edit = client.get(f'/budgets/{b_id}/edit')
    assert resp_edit.status_code == 404

    # Try to delete User 1's budget -> 404
    resp_del = client.post(f'/budgets/{b_id}/delete')
    assert resp_del.status_code == 404

    with app.app_context():
        intact_b = db.session.get(Budget, b_id)
        assert intact_b is not None
