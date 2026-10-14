"""
Seed demo data for ALTO Personal Finance Tracker.
Creates a demo user with realistic sample transactions and budgets
for portfolio demonstrations and presentations.

Usage:
    python seed_demo_data.py
"""
from datetime import date, timedelta
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import User, Transaction, Budget

app = create_app('development')

with app.app_context():
    print("Initializing demo dataset for ALTO...")

    # Check if demo user already exists
    demo_email = "demo@alto.app"
    user = User.query.filter_by(email=demo_email).first()

    if not user:
        user = User(
            name="Aditi Sharma",
            email=demo_email,
            currency="₹"
        )
        user.set_password("alto1234")
        db.session.add(user)
        db.session.commit()
        print(f"Created demo user: {demo_email} (Password: alto1234)")
    else:
        print(f"Demo user {demo_email} already exists. Refreshing transactions and budgets...")
        # Clear existing transactions and budgets for clean demo state
        Transaction.query.filter_by(user_id=user.id).delete()
        Budget.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    today = date.today()
    curr_month = today.month
    curr_year = today.year

    # 1. Sample Budgets for Current Month
    budgets_data = [
        ("Housing & Rent", Decimal("18000.00")),
        ("Groceries & Food", Decimal("9000.00")),
        ("Dining Out & Cafes", Decimal("4500.00")),
        ("Transportation & Fuel", Decimal("4000.00")),
        ("Utilities & Bills", Decimal("3500.00")),
        ("Entertainment & Subscriptions", Decimal("2000.00")),
        ("Shopping & Personal Care", Decimal("5000.00"))
    ]

    for cat, limit in budgets_data:
        b = Budget(
            user_id=user.id,
            category=cat,
            monthly_limit=limit,
            month=curr_month,
            year=curr_year
        )
        db.session.add(b)

    db.session.commit()
    print("Configured monthly budget targets.")

    # 2. Sample Incomes for Current Month and Past Months
    transactions = [
        # Incomes
        Transaction(
            user_id=user.id,
            transaction_type="income",
            amount=Decimal("65000.00"),
            category="Salary",
            description="Monthly Software Engineer Paycheck",
            payment_method="Net Banking",
            transaction_date=date(curr_year, curr_month, 1)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="income",
            amount=Decimal("12500.00"),
            category="Freelance / Consulting",
            description="Frontend UI Design project milestone",
            payment_method="UPI / Instant Pay",
            transaction_date=date(curr_year, curr_month, 5)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="income",
            amount=Decimal("2400.00"),
            category="Investments & Dividends",
            description="Quarterly index fund dividend payout",
            payment_method="Net Banking",
            transaction_date=date(curr_year, curr_month, 10)
        ),

        # Expenses
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("18000.00"),
            category="Housing & Rent",
            description="Apartment rent payment",
            payment_method="Net Banking",
            transaction_date=date(curr_year, curr_month, 2)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("3850.00"),
            category="Groceries & Food",
            description="Weekly Nature's Basket supermarket run",
            payment_method="UPI / Instant Pay",
            transaction_date=date(curr_year, curr_month, 4)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("4100.00"),
            category="Dining Out & Cafes",
            description="Weekend dinner with college friends (Reaches 91% of budget limit)",
            payment_method="Credit Card",
            transaction_date=date(curr_year, curr_month, 7)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("2150.00"),
            category="Transportation & Fuel",
            description="Metro pass recharge & fuel refill",
            payment_method="UPI / Instant Pay",
            transaction_date=date(curr_year, curr_month, 8)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("2350.00"),
            category="Entertainment & Subscriptions",
            description="Netflix, Spotify & cloud storage subscriptions (Exceeds limit!)",
            payment_method="Credit Card",
            transaction_date=date(curr_year, curr_month, 11)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("1800.00"),
            category="Utilities & Bills",
            description="High-speed fiber broadband bill",
            payment_method="UPI / Instant Pay",
            transaction_date=date(curr_year, curr_month, 12)
        ),
        Transaction(
            user_id=user.id,
            transaction_type="expense",
            amount=Decimal("2800.00"),
            category="Shopping & Personal Care",
            description="Work desk accessories and ergonomics",
            payment_method="Debit Card",
            transaction_date=date(curr_year, curr_month, 13)
        ),
    ]

    # Add historical data for past 3 months so the 6-month chart looks lively
    for offset_months in [1, 2, 3]:
        prev_month_raw = curr_month - offset_months
        prev_year = curr_year
        if prev_month_raw <= 0:
            prev_month_raw += 12
            prev_year -= 1

        transactions.extend([
            Transaction(
                user_id=user.id,
                transaction_type="income",
                amount=Decimal("65000.00"),
                category="Salary",
                description="Monthly Salary",
                payment_method="Net Banking",
                transaction_date=date(prev_year, prev_month_raw, 1)
            ),
            Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("18000.00"),
                category="Housing & Rent",
                description="Rent payment",
                payment_method="Net Banking",
                transaction_date=date(prev_year, prev_month_raw, 2)
            ),
            Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("7500.00") + Decimal(str(offset_months * 400)),
                category="Groceries & Food",
                description="Monthly groceries",
                payment_method="UPI / Instant Pay",
                transaction_date=date(prev_year, prev_month_raw, 15)
            ),
            Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("3500.00"),
                category="Transportation & Fuel",
                description="Commute expenses",
                payment_method="UPI / Instant Pay",
                transaction_date=date(prev_year, prev_month_raw, 20)
            )
        ])

    for t in transactions:
        db.session.add(t)

    db.session.commit()
    print(f"Successfully populated {len(transactions)} realistic transactions!")
    print("=" * 60)
    print("DEMO CREDENTIALS:")
    print("  Email:    demo@alto.app")
    print("  Password: alto1234")
    print("=" * 60)
