"""
Database models for ALTO Personal Finance Tracker.
Defines User, Transaction, and Budget models using SQLAlchemy ORM.
"""
from datetime import datetime, date, timezone
from decimal import Decimal
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Callback function used by Flask-Login to reload the user object from the session."""
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    """
    User model representing an account holder in ALTO.
    Stores authentication credentials, currency preference, and relationships
    to transactions and monthly budgets.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='₹')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships: If a user is deleted, all their transactions and budgets are cascade deleted
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes the password securely using werkzeug scrypt/pbkdf2."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the plain password against the stored secure hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Transaction(db.Model):
    """
    Transaction model representing a single financial movement (Income or Expense).
    Stores amount, category, payment method, date, and user ownership.
    """
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash')
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Pre-defined categories for convenience and consistency
    INCOME_CATEGORIES = [
        'Salary',
        'Freelance / Consulting',
        'Investments & Dividends',
        'Allowance / Stipend',
        'Business / Side Hustle',
        'Gifts',
        'Refunds & Cashbacks',
        'Other Income'
    ]

    EXPENSE_CATEGORIES = [
        'Housing & Rent',
        'Groceries & Food',
        'Dining Out & Cafes',
        'Transportation & Fuel',
        'Utilities & Bills',
        'Healthcare & Medical',
        'Education & Books',
        'Entertainment & Subscriptions',
        'Shopping & Personal Care',
        'Travel & Vacation',
        'Debt & Loans',
        'Investments & Savings',
        'Other Expense'
    ]

    PAYMENT_METHODS = [
        'Cash',
        'UPI / Instant Pay',
        'Debit Card',
        'Credit Card',
        'Net Banking',
        'Cheque',
        'Digital Wallet'
    ]

    def to_dict(self):
        """Serializes the transaction into a dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'category': self.category,
            'description': self.description or '',
            'payment_method': self.payment_method,
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Transaction {self.transaction_type} {self.amount} ({self.category})>'


class Budget(db.Model):
    """
    Budget model representing a monthly spending limit for a specific category.
    Includes month (1-12) and year to allow historical tracking and future planning.
    """
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False)
    monthly_limit = db.Column(db.Numeric(12, 2), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 to 12
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='uq_user_category_month_year'),
    )

    def calculate_spent_and_remaining(self):
        """
        Calculates the actual expenses in this budget's category for its specific month and year,
        along with the remaining balance and percentage spent.
        """
        # Sum expenses in this user's category for the target month and year
        expenses = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_type == 'expense',
            Transaction.category == self.category,
            db.extract('month', Transaction.transaction_date) == self.month,
            db.extract('year', Transaction.transaction_date) == self.year
        ).all()

        spent = sum(Decimal(str(exp.amount)) for exp in expenses) if expenses else Decimal('0.00')
        limit = Decimal(str(self.monthly_limit))
        remaining = limit - spent
        percent_spent = float((spent / limit) * 100) if limit > 0 else 0.0

        # Status flag
        if percent_spent > 100:
            status = 'exceeded'
        elif percent_spent >= 80:
            status = 'warning'
        else:
            status = 'healthy'

        return {
            'spent': float(spent),
            'limit': float(limit),
            'remaining': float(remaining),
            'percent_spent': min(percent_spent, 100.0),
            'raw_percent': percent_spent,
            'status': status
        }

    def __repr__(self):
        return f'<Budget {self.category} {self.month}/{self.year}: limit {self.monthly_limit}>'
