"""
Budgets routes for ALTO.
Handles budget creation, viewing, editing, deletion, and monthly spending comparisons.
"""
from datetime import date
from decimal import Decimal
import calendar
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.budgets import budgets_bp
from app.extensions import db
from app.models import Budget, Transaction
from app.forms import BudgetForm


@budgets_bp.route('/budgets')
@login_required
def index():
    """List monthly budgets with actual spending progress and alerts."""
    today = date.today()

    try:
        selected_month = int(request.args.get('month', today.month))
        selected_year = int(request.args.get('year', today.year))
        if selected_month < 1 or selected_month > 12:
            selected_month = today.month
    except (ValueError, TypeError):
        selected_month = today.month
        selected_year = today.year

    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).order_by(Budget.category.asc()).all()

    budget_items = []
    total_budgeted = Decimal('0.00')
    total_spent = Decimal('0.00')
    warning_count = 0
    exceeded_count = 0

    for b in budgets:
        metrics = b.calculate_spent_and_remaining()
        budget_items.append({
            'budget': b,
            'metrics': metrics
        })
        total_budgeted += Decimal(str(metrics['limit']))
        total_spent += Decimal(str(metrics['spent']))
        if metrics['status'] == 'warning':
            warning_count += 1
        elif metrics['status'] == 'exceeded':
            exceeded_count += 1

    total_remaining = total_budgeted - total_spent
    overall_percentage = float((total_spent / total_budgeted) * 100) if total_budgeted > 0 else 0.0

    months_list = [(m, calendar.month_name[m]) for m in range(1, 13)]
    years_list = list(range(today.year - 2, today.year + 4))

    return render_template(
        'budgets/list.html',
        title='Monthly Budgets',
        budget_items=budget_items,
        selected_month=selected_month,
        selected_year=selected_year,
        month_name=calendar.month_name[selected_month],
        total_budgeted=total_budgeted,
        total_spent=total_spent,
        total_remaining=total_remaining,
        overall_percentage=min(overall_percentage, 100.0),
        raw_overall_percentage=overall_percentage,
        warning_count=warning_count,
        exceeded_count=exceeded_count,
        months_list=months_list,
        years_list=years_list
    )


@budgets_bp.route('/budgets/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new monthly spending limit."""
    form = BudgetForm()

    # Pre-select month and year if passed in query string
    if request.method == 'GET':
        if request.args.get('month'):
            form.month.data = int(request.args.get('month'))
        if request.args.get('year'):
            form.year.data = int(request.args.get('year'))

    if form.validate_on_submit():
        budget = Budget(
            user_id=current_user.id,
            category=form.category.data,
            monthly_limit=Decimal(str(form.monthly_limit.data)),
            month=int(form.month.data),
            year=int(form.year.data)
        )
        db.session.add(budget)
        db.session.commit()

        flash(f'Budget for {form.category.data} ({calendar.month_name[budget.month]} {budget.year}) created!', 'success')
        return redirect(url_for('budgets.index', month=budget.month, year=budget.year))

    return render_template('budgets/form.html', title='Set Budget', form=form, is_edit=False)


@budgets_bp.route('/budgets/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing monthly budget limit."""
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)

    if request.method == 'GET':
        form.budget_id.data = str(budget.id)

    if form.validate_on_submit():
        budget.category = form.category.data
        budget.monthly_limit = Decimal(str(form.monthly_limit.data))
        budget.month = int(form.month.data)
        budget.year = int(form.year.data)

        db.session.commit()
        flash(f'Budget for {budget.category} updated successfully!', 'success')
        return redirect(url_for('budgets.index', month=budget.month, year=budget.year))

    return render_template('budgets/form.html', title='Edit Budget', form=form, budget=budget, is_edit=True)


@budgets_bp.route('/budgets/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a budget. Enforces user ownership and CSRF protection."""
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    month = budget.month
    year = budget.year
    db.session.delete(budget)
    db.session.commit()

    flash('Budget deleted successfully.', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))
