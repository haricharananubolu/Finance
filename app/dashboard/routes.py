"""
Dashboard routes for ALTO.
Calculates core financial metrics, generates chart datasets, and displays budget progress.
"""
from datetime import date, datetime
from decimal import Decimal
import calendar
from flask import render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.dashboard import dashboard_bp
from app.extensions import db
from app.models import Transaction, Budget
from app.forms import TransactionForm


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main user financial dashboard."""
    today = date.today()

    # Parse month and year from query params, or default to current date
    try:
        selected_month = int(request.args.get('month', today.month))
        selected_year = int(request.args.get('year', today.year))
        if selected_month < 1 or selected_month > 12:
            selected_month = today.month
    except (ValueError, TypeError):
        selected_month = today.month
        selected_year = today.year

    # 1. All-time calculations
    all_income_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'income'
    ).scalar()

    all_expense_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense'
    ).scalar()

    all_time_balance = Decimal(str(all_income_sum)) - Decimal(str(all_expense_sum))

    # 2. Selected Month Financials
    month_income_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'income',
        extract('month', Transaction.transaction_date) == selected_month,
        extract('year', Transaction.transaction_date) == selected_year
    ).scalar()

    month_expense_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense',
        extract('month', Transaction.transaction_date) == selected_month,
        extract('year', Transaction.transaction_date) == selected_year
    ).scalar()

    month_income = Decimal(str(month_income_sum))
    month_expense = Decimal(str(month_expense_sum))
    month_savings = month_income - month_expense

    if month_income > 0:
        savings_rate = float((month_savings / month_income) * 100)
    else:
        savings_rate = 0.0

    # 3. Recent 5 Transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())\
        .limit(5).all()

    # 4. Expense Breakdown by Category for Selected Month
    category_breakdown_raw = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense',
        extract('month', Transaction.transaction_date) == selected_month,
        extract('year', Transaction.transaction_date) == selected_year
    ).group_by(Transaction.category)\
     .order_by(func.sum(Transaction.amount).desc()).all()

    category_labels = [row[0] for row in category_breakdown_raw]
    category_data = [float(row[1]) for row in category_breakdown_raw]

    # 5. Monthly Trend (Past 6 Months)
    trend_labels = []
    trend_income = []
    trend_expenses = []

    # Calculate past 6 months backwards from current month
    for i in range(5, -1, -1):
        # Calculate target month and year
        target_month_raw = today.month - i
        target_year = today.year
        if target_month_raw <= 0:
            target_month_raw += 12
            target_year -= 1

        month_label = f"{calendar.month_abbr[target_month_raw]} {str(target_year)[2:]}"
        trend_labels.append(month_label)

        inc = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == 'income',
            extract('month', Transaction.transaction_date) == target_month_raw,
            extract('year', Transaction.transaction_date) == target_year
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == 'expense',
            extract('month', Transaction.transaction_date) == target_month_raw,
            extract('year', Transaction.transaction_date) == target_year
        ).scalar()

        trend_income.append(float(inc))
        trend_expenses.append(float(exp))

    # 6. Budgets for Selected Month
    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).all()

    budgets_progress = []
    for b in budgets:
        metrics = b.calculate_spent_and_remaining()
        budgets_progress.append({
            'budget': b,
            'metrics': metrics
        })

    # Available months list for selector
    months_list = [(m, calendar.month_name[m]) for m in range(1, 13)]
    years_list = list(range(today.year - 2, today.year + 3))

    # Transaction quick form for modal
    quick_form = TransactionForm()

    return render_template(
        'dashboard/dashboard.html',
        title='Dashboard',
        all_time_balance=all_time_balance,
        month_income=month_income,
        month_expense=month_expense,
        month_savings=month_savings,
        savings_rate=savings_rate,
        recent_transactions=recent_transactions,
        category_labels=category_labels,
        category_data=category_data,
        trend_labels=trend_labels,
        trend_income=trend_income,
        trend_expenses=trend_expenses,
        budgets_progress=budgets_progress,
        selected_month=selected_month,
        selected_year=selected_year,
        month_name=calendar.month_name[selected_month],
        months_list=months_list,
        years_list=years_list,
        quick_form=quick_form
    )
