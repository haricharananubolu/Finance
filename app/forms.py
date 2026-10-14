"""
Form definitions for ALTO using Flask-WTF and WTForms.
Includes comprehensive server-side validation, clean error messages, and CSRF protection.
"""
from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DecimalField,
    SelectField,
    DateField,
    TextAreaField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
    Optional
)
from flask_login import current_user
from app.models import User, Transaction, Budget
from decimal import Decimal


class RegistrationForm(FlaskForm):
    """User account registration form."""
    name = StringField('Full Name', validators=[
        DataRequired(message='Please enter your full name.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Please enter your email address.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please create a password.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        """Verify the email isn't already registered."""
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email address already exists. Please log in.')


class LoginForm(FlaskForm):
    """User login authentication form."""
    email = StringField('Email Address', validators=[
        DataRequired(message='Please enter your registered email.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password.')
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TransactionForm(FlaskForm):
    """Add / Edit income or expense transaction form."""
    transaction_type = SelectField('Transaction Type', choices=[
        ('expense', 'Expense (- Cash Out)'),
        ('income', 'Income (+ Cash In)')
    ], validators=[DataRequired(message='Please select a transaction type.')])

    amount = DecimalField('Amount', places=2, validators=[
        InputRequired(message='Please enter an amount.')
    ])

    category = SelectField('Category', choices=[], validators=[
        DataRequired(message='Please select a category.')
    ])

    description = StringField('Description / Notes', validators=[
        Optional(),
        Length(max=255, message='Description must be under 255 characters.')
    ])

    payment_method = SelectField('Payment Method', choices=[
        (method, method) for method in Transaction.PAYMENT_METHODS
    ], validators=[DataRequired(message='Please select a payment method.')])

    transaction_date = DateField('Date', default=date.today, validators=[
        DataRequired(message='Please enter a valid date.')
    ])

    submit = SubmitField('Save Transaction')

    def validate_amount(self, field):
        if field.data is None or field.data <= Decimal('0.00'):
            raise ValidationError('Amount must be greater than 0.00.')

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        all_categories = sorted(list(set(Transaction.EXPENSE_CATEGORIES + Transaction.INCOME_CATEGORIES)))
        self.category.choices = [(c, c) for c in all_categories]


class BudgetForm(FlaskForm):
    """Monthly budget creation and modification form."""
    category = SelectField('Expense Category', choices=[
        (c, c) for c in Transaction.EXPENSE_CATEGORIES
    ], validators=[DataRequired(message='Please select an expense category.')])

    monthly_limit = DecimalField('Monthly Spending Limit', places=2, validators=[
        InputRequired(message='Please enter a spending limit.')
    ])

    month = SelectField('Month', coerce=int, choices=[
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ], default=date.today().month, validators=[DataRequired()])

    year = SelectField('Year', coerce=int, choices=[
        (y, str(y)) for y in range(date.today().year - 2, date.today().year + 5)
    ], default=date.today().year, validators=[DataRequired()])

    budget_id = HiddenField()
    submit = SubmitField('Save Budget')

    def validate_monthly_limit(self, field):
        if field.data is None or field.data < Decimal('1.00'):
            raise ValidationError('Monthly limit must be at least 1.00.')

    def validate_category(self, field):
        """Ensure the user doesn't already have an active budget for this category, month, and year."""
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category=field.data,
            month=int(self.month.data),
            year=int(self.year.data)
        ).first()

        # If editing, ignore the existing record if it is the current budget itself
        if existing and (not self.budget_id.data or str(existing.id) != str(self.budget_id.data)):
            raise ValidationError(f'You already have a budget set for {field.data} in {self.month.data}/{self.year.data}. You can edit it instead.')


class UpdateProfileForm(FlaskForm):
    """Form to update user display name and currency."""
    name = StringField('Full Name', validators=[
        DataRequired(message='Name cannot be empty.'),
        Length(min=2, max=100)
    ])
    currency = SelectField('Preferred Currency Symbol', choices=[
        ('₹', '₹ INR (Indian Rupee)'),
        ('$', '$ USD (US Dollar)'),
        ('€', '€ EUR (Euro)'),
        ('£', '£ GBP (British Pound)'),
        ('¥', '¥ JPY / CNY (Yen / Yuan)'),
        ('AED', 'AED (UAE Dirham)'),
        ('CAD', 'CAD (Canadian Dollar)'),
        ('AUD', 'AUD (Australian Dollar)')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Profile Settings')


class ChangePasswordForm(FlaskForm):
    """Form to change password securely with verification of current password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Please enter your current password.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='Please enter a new password.'),
        Length(min=6, message='New password must be at least 6 characters long.')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='New passwords must match.')
    ])
    submit = SubmitField('Update Password')

    def validate_current_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect.')
