"""
Authentication routes for ALTO.
Handles user registration, login, and logout.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
from app.auth import auth_bp
from app.extensions import db
from app.models import User
from app.forms import RegistrationForm, LoginForm


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account with hashed password."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            currency='₹'  # Default currency is Indian Rupee
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your ALTO account has been created successfully! Please sign in to continue.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Create Account', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate existing users and redirect to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')

            # Validate next URL to prevent open redirect vulnerabilities
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please double check and try again.', 'danger')

    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user session."""
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))
