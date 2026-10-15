"""
Application factory for ALTO.
Initializes the Flask application, registers blueprints, database extensions,
custom Jinja filters, context processors, and global error handlers.
"""
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name='development'):
    """Construct the core Flask application instance."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Ensure the instance folder exists for SQLite storage
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    # Initialize extensions with the application
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.transactions import transactions_bp
    from app.budgets import budgets_bp
    from app.reports import reports_bp
    from app.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(profile_bp)

    # Landing page route
    @app.route('/')
    def index():
        """Public landing page showcasing ALTO features and value proposition."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html', title='Take Control of Your Money')

    # Custom Jinja Filters
    @app.template_filter('currency')
    def currency_filter(amount, symbol=None):
        """Formats a float or Decimal as a clean currency string."""
        if amount is None:
            return '—'
        try:
            val = float(amount)
        except (ValueError, TypeError):
            return '—'

        curr = symbol if symbol else (current_user.currency if current_user.is_authenticated else '₹')
        # Format with thousand separators and 2 decimal places
        formatted = f"{val:,.2f}"
        return f"{curr} {formatted}"

    @app.template_filter('date_format')
    def date_filter(d, fmt='%d %b %Y'):
        """Formats a date object or string into a human-readable format."""
        if not d:
            return ''
        if isinstance(d, (datetime, date)):
            return d.strftime(fmt)
        try:
            parsed = datetime.strptime(str(d), '%Y-%m-%d')
            return parsed.strftime(fmt)
        except Exception:
            return str(d)

    # Global Context Processors
    @app.context_processor
    def inject_global_data():
        """Injects frequently needed variables into all Jinja templates."""
        return {
            'current_year': datetime.now().year,
            'today': date.today(),
            'app_name': 'ALTO'
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', title='Access Forbidden'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', title='Server Error'), 500

    # Initialize Database Tables
    with app.app_context():
        db.create_all()

    return app


# Expose default WSGI callable so `gunicorn app:app` succeeds automatically
app = create_app(os.environ.get('FLASK_ENV', 'production'))
