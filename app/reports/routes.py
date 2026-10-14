"""
Reports routes for ALTO.
Generates comprehensive financial summaries, category breakdowns, monthly trends,
and handles secure CSV export of user transaction records.
"""
import io
import csv
from datetime import datetime, date, timedelta
from decimal import Decimal
from flask import render_template, request, Response, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.reports import reports_bp
from app.extensions import db
from app.models import Transaction


@reports_bp.route('/reports')
@login_required
def index():
    """Financial reporting dashboard with customizable date filters and charts."""
    today = date.today()
    preset = request.args.get('preset', 'this_month')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    # Determine start and end dates based on preset or custom inputs
    if preset == 'this_month':
        start_date = date(today.year, today.month, 1)
        # Last day of current month
        if today.month == 12:
            end_date = date(today.year, 12, 31)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
    elif preset == 'last_month':
        if today.month == 1:
            start_date = date(today.year - 1, 12, 1)
            end_date = date(today.year - 1, 12, 31)
        else:
            start_date = date(today.year, today.month - 1, 1)
            end_date = date(today.year, today.month, 1) - timedelta(days=1)
    elif preset == 'this_year':
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
    elif preset == 'all_time':
        start_date = date(2000, 1, 1)
        end_date = date(today.year + 5, 12, 31)
    elif preset == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = date(today.year, today.month, 1)
            end_date = today
    else:
        preset = 'this_month'
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year, 12, 31)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Base query for the period restricted strictly to current authenticated user
    base_query = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    )

    transactions = base_query.order_by(Transaction.transaction_date.desc()).all()

    # Core Financial Totals for the period
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_savings = total_income - total_expenses
    savings_rate = float((net_savings / total_income) * 100) if total_income > 0 else 0.0

    # Category breakdown for expenses
    expense_categories_map = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            expense_categories_map[t.category] = expense_categories_map.get(t.category, Decimal('0.00')) + t.amount

    # Sort categories by spending descending
    sorted_expense_categories = sorted(expense_categories_map.items(), key=lambda x: x[1], reverse=True)
    cat_labels = [k for k, v in sorted_expense_categories]
    cat_values = [float(v) for k, v in sorted_expense_categories]
    cat_percentages = [
        round((float(v) / float(total_expenses) * 100), 1) if total_expenses > 0 else 0
        for k, v in sorted_expense_categories
    ]

    # Payment method breakdown
    payment_methods_map = {}
    for t in transactions:
        payment_methods_map[t.payment_method] = payment_methods_map.get(t.payment_method, Decimal('0.00')) + t.amount
    payment_labels = list(payment_methods_map.keys())
    payment_values = [float(v) for v in payment_methods_map.values()]

    return render_template(
        'reports/reports.html',
        title='Financial Reports & Analytics',
        preset=preset,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        transaction_count=len(transactions),
        cat_labels=cat_labels,
        cat_values=cat_values,
        cat_percentages=cat_percentages,
        category_rows=zip(cat_labels, cat_values, cat_percentages),
        payment_labels=payment_labels,
        payment_values=payment_values,
        transactions=transactions
    )


@reports_bp.route('/reports/export-csv')
@login_required
def export_csv():
    """
    Export current user's transactions as a downloadable CSV file.
    Only records belonging to the authenticated user are exported.
    """
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    trans_type = request.args.get('type', '').strip().lower()

    query = Transaction.query.filter_by(user_id=current_user.id)

    if start_date_str:
        try:
            sd = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= sd)
        except ValueError:
            pass

    if end_date_str:
        try:
            ed = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= ed)
        except ValueError:
            pass

    if trans_type in ['income', 'expense']:
        query = query.filter(Transaction.transaction_type == trans_type)

    transactions = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).all()

    # Generate CSV stream in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        'Transaction ID',
        'Date',
        'Type',
        'Category',
        'Amount',
        'Currency',
        'Payment Method',
        'Description',
        'Created At'
    ])

    for t in transactions:
        writer.writerow([
            t.id,
            t.transaction_date.strftime('%Y-%m-%d'),
            t.transaction_type.capitalize(),
            t.category,
            f"{t.amount:.2f}",
            current_user.currency,
            t.payment_method,
            t.description or '',
            t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    filename = f"alto_transactions_{current_user.name.replace(' ', '_').lower()}_{date.today().strftime('%Y%m%d')}.csv"

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
