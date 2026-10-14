"""
Transactions routes for ALTO.
Handles transaction creation, viewing, filtering, sorting, pagination, editing, and deletion.
"""
from datetime import datetime, date
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.transactions import transactions_bp
from app.extensions import db
from app.models import Transaction
from app.forms import TransactionForm


@transactions_bp.route('/transactions')
@login_required
def index():
    """List transactions with filtering, searching, sorting, and pagination."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('type', '').strip().lower()
    category = request.args.get('category', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    sort_by = request.args.get('sort_by', 'date_desc').strip()

    # Base query restricted strictly to current authenticated user
    query = Transaction.query.filter_by(user_id=current_user.id)

    # 1. Search filter (description, category, or payment method)
    if search_query:
        query = query.filter(
            (Transaction.description.ilike(f'%{search_query}%')) |
            (Transaction.category.ilike(f'%{search_query}%')) |
            (Transaction.payment_method.ilike(f'%{search_query}%'))
        )

    # 2. Type filter ('income' or 'expense')
    if trans_type in ['income', 'expense']:
        query = query.filter(Transaction.transaction_type == trans_type)

    # 3. Category filter
    if category:
        query = query.filter(Transaction.category == category)

    # 4. Date range filter
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= sd)
        except ValueError:
            pass

    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= ed)
        except ValueError:
            pass

    # 5. Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())
    else:  # Default to 'date_desc'
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    # 6. Pagination
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items

    # Available categories for the filter dropdown
    all_categories = sorted(list(set(Transaction.EXPENSE_CATEGORIES + Transaction.INCOME_CATEGORIES)))

    # Calculate filtered summary metrics
    filtered_income = sum(t.amount for t in query.all() if t.transaction_type == 'income')
    filtered_expense = sum(t.amount for t in query.all() if t.transaction_type == 'expense')
    filtered_net = filtered_income - filtered_expense

    return render_template(
        'transactions/list.html',
        title='Transactions',
        transactions=transactions,
        pagination=pagination,
        search_query=search_query,
        trans_type=trans_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        all_categories=all_categories,
        filtered_income=filtered_income,
        filtered_expense=filtered_expense,
        filtered_net=filtered_net
    )


@transactions_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new transaction (income or expense)."""
    form = TransactionForm()

    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type=form.transaction_type.data,
            amount=Decimal(str(form.amount.data)),
            category=form.category.data,
            description=form.description.data.strip() if form.description.data else '',
            payment_method=form.payment_method.data,
            transaction_date=form.transaction_date.data
        )
        db.session.add(transaction)
        db.session.commit()

        flash(f'Successfully added {form.transaction_type.data.capitalize()} transaction of {current_user.currency} {form.amount.data}!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template(
        'transactions/form.html',
        title='Add Transaction',
        form=form,
        is_edit=False,
        income_categories=Transaction.INCOME_CATEGORIES,
        expense_categories=Transaction.EXPENSE_CATEGORIES
    )


@transactions_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing transaction. Enforces user ownership."""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        transaction.transaction_type = form.transaction_type.data
        transaction.amount = Decimal(str(form.amount.data))
        transaction.category = form.category.data
        transaction.description = form.description.data.strip() if form.description.data else ''
        transaction.payment_method = form.payment_method.data
        transaction.transaction_date = form.transaction_date.data

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template(
        'transactions/form.html',
        title='Edit Transaction',
        form=form,
        transaction=transaction,
        is_edit=True,
        income_categories=Transaction.INCOME_CATEGORIES,
        expense_categories=Transaction.EXPENSE_CATEGORIES
    )


@transactions_bp.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a transaction. Enforces user ownership and CSRF protection."""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()

    flash('Transaction has been deleted.', 'info')
    return redirect(request.referrer or url_for('transactions.index'))
