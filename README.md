# ALTO — Full-Stack Personal Finance Tracker

<div align="center">
  <h3>▲ Take Control of Your Money</h3>
  <p><strong>A Modern, Full-Stack Personal Finance Web Application Built with Python, Flask, SQLAlchemy, SQLite, and Vanilla JavaScript.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12">
    <img src="https://img.shields.io/badge/Framework-Flask_3.0-lightgrey.svg" alt="Flask 3.0">
    <img src="https://img.shields.io/badge/Database-SQLite_%2F_SQLAlchemy-green.svg" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/Security-CSRF_%26_Werkzeug_Hashing-red.svg" alt="Security">
    <img src="https://img.shields.io/badge/Tests-19%20Passed-brightgreen.svg" alt="Pytest">
  </p>
</div>

---

## 1. Project Overview

**ALTO** is a complete, production-grade personal finance management web application designed to help individuals, students, and professionals track cash flows, enforce monthly category budgets, analyze spending trends, and build disciplined financial habits.

### Key Capabilities:
- **Real-Time Financial Dashboard:** Calculates all-time net balance, selected month income, expenses, net savings, and savings percentage dynamically from the database.
- **Interactive Visualizations:** Dual 6-month comparative cash flow bar chart and expense category distribution donut chart powered by Chart.js.
- **Transaction Management:** Full CRUD operations for income and expenses with pagination, sorting, live category filtering, and keyword search.
- **Monthly Category Budgets:** Visual progress meters that automatically switch status:
  - **Healthy:** Spending < 80% of limit
  - **Caution (Amber Warning):** Spending reaches 80% – 100% of limit
  - **Exceeded (Rose Alert):** Spending breaches 100% of limit
- **Reports & Analytics:** Period presets (This Month, Last Month, This Year, All Time) and custom date ranges with payment method breakdown and print-ready summary.
- **One-Click CSV Export:** Secure export of transaction records strictly isolated to the authenticated user.
- **User Customization:** Preferred currency symbol configuration (default **₹ INR**, supports $, €, £, ¥, AED, etc.) and secure password modification.
- **Robust Security:** Werkzeug password hashing, per-user data isolation on every SQL query, CSRF form protection via Flask-WTF, and parameter validation.

---

## 2. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.12, Flask 3.0.3, Werkzeug, Jinja2 |
| **Database & ORM** | SQLite, SQLAlchemy 2.0 (Flask-SQLAlchemy 3.1) |
| **Authentication** | Flask-Login 0.6.3 with secure session cookies |
| **Forms & CSRF** | Flask-WTF 1.2.1, WTForms 3.1.2, email-validator |
| **Frontend** | HTML5, CSS3 (Modern SaaS Design System), Vanilla JavaScript |
| **Charts** | Chart.js 4.4 |
| **Testing** | pytest 8.2 (19 automated unit & integration tests) |
| **Config & Env** | python-dotenv |

---

## 3. Architecture & Project Structure

The project follows the standard **Flask Application Factory** pattern organized with modular **Blueprints**:

```
alto/
│
├── app/
│   ├── __init__.py           # Application factory (create_app), Jinja filters & error handlers
│   ├── extensions.py         # Centralized extensions (db, login_manager, csrf)
│   ├── models.py             # SQLAlchemy models (User, Transaction, Budget)
│   ├── forms.py              # WTForms classes with server-side validation & CSRF
│   │
│   ├── auth/                 # Authentication Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Register, Login, Logout
│   │
│   ├── dashboard/            # Dashboard Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Real-time financial calculations & Chart.js data
│   │
│   ├── transactions/         # Transactions Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # CRUD, filtering, sorting, search & pagination
│   │
│   ├── budgets/              # Budgets Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Category limits, spent tracking & warning alerts
│   │
│   ├── reports/              # Reports & Analytics Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Period analytics, payment channels & CSV export
│   │
│   ├── profile/              # Settings Blueprint
│   │   ├── __init__.py
│   │   └── routes.py         # Display name, currency preference & password change
│   │
│   ├── templates/            # Jinja2 HTML Templates
│   │   ├── base.html         # SaaS shell, desktop sidebar, mobile drawer, toasts & modals
│   │   ├── index.html        # Public landing page with hero, features & preview
│   │   ├── auth/             # login.html, register.html
│   │   ├── dashboard/        # dashboard.html
│   │   ├── transactions/     # list.html, form.html
│   │   ├── budgets/          # list.html, form.html
│   │   ├── reports/          # reports.html
│   │   ├── profile/          # profile.html
│   │   └── errors/           # 404.html, 403.html, 500.html
│   │
│   └── static/               # Static Assets
│       ├── css/
│       │   └── style.css     # Master design system (slate/navy palette, responsive grids)
│       └── js/
│           ├── main.js       # Drawer toggle, modals, dynamic dropdowns, auto-dismiss alerts
│           └── dashboard.js  # Chart.js initialization (trend bars & category doughnut)
│
├── tests/                    # Automated Test Suite (pytest)
│   ├── conftest.py           # In-memory test db, test clients, user fixtures
│   ├── test_auth.py          # Registration, login, logout, protected routes
│   ├── test_transactions.py  # Inflows, outflows, edit, delete, data isolation
│   ├── test_budgets.py       # Limits, progress percentage, 80% & 100% status thresholds
│   └── test_live_flow.py     # End-to-end CSRF and session integration flow
│
├── config.py                 # Development, Testing, and Production configurations
├── run.py                    # Application entry point script
├── seed_demo_data.py         # Script to populate realistic demo account with 20+ transactions
├── requirements.txt          # Pinned Python package dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore specifications
└── README.md                 # Complete documentation & presentation guide
```

---

## 4. Local Setup Guide (Windows & VS Code)

Follow these step-by-step commands in **PowerShell** or **Command Prompt** in VS Code:

### Step 1: Open the Project Directory
```powershell
cd C:\Users\satvi\.gemini\antigravity\scratch\alto
```

### Step 2: Create and Activate a Python Virtual Environment
```powershell
# Create the virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# (If PowerShell blocks script execution, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

The default values in `.env` are ready for local development:
```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=alto-dev-super-secret-key-capstone-2026-secure
DATABASE_URL=sqlite:///alto.db
```

### Step 5: Seed Demo Data (Recommended for Presentations)
Run the automated seed script to populate a rich demo account with 22 realistic transactions and 7 monthly budget targets:
```powershell
python seed_demo_data.py
```

**Demo Account Credentials:**
- **Email:** `demo@alto.app`
- **Password:** `alto1234`

### Step 6: Start the Development Server
```powershell
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Running Automated Tests

Run the full pytest suite to verify all 19 unit, integration, and security test cases:

```powershell
pytest -v
```

**Output:**
```
============================= test session starts =============================
collected 19 items

tests/test_auth.py::test_landing_page PASSED                             [  5%]
tests/test_auth.py::test_registration_success PASSED                     [ 10%]
tests/test_auth.py::test_registration_duplicate_email PASSED             [ 15%]
tests/test_auth.py::test_registration_password_mismatch PASSED           [ 21%]
tests/test_auth.py::test_login_success PASSED                            [ 26%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 31%]
tests/test_auth.py::test_login_nonexistent_user PASSED                   [ 36%]
tests/test_auth.py::test_logout PASSED                                   [ 42%]
tests/test_auth.py::test_protected_routes_require_login PASSED           [ 47%]
tests/test_budgets.py::test_create_budget PASSED                         [ 52%]
tests/test_budgets.py::test_budget_calculations_and_status PASSED        [ 57%]
tests/test_budgets.py::test_user_budget_isolation PASSED                 [ 63%]
tests/test_live_flow.py::test_csrf_and_full_user_flow PASSED             [ 68%]
tests/test_transactions.py::test_create_income_transaction PASSED        [ 73%]
tests/test_transactions.py::test_create_expense_transaction PASSED       [ 78%]
tests/test_transactions.py::test_edit_transaction PASSED                 [ 84%]
tests/test_transactions.py::test_delete_transaction PASSED               [ 89%]
tests/test_transactions.py::test_user_transaction_isolation PASSED       [ 94%]
tests/test_transactions.py::test_invalid_transaction_amount PASSED       [100%]

============================= 19 passed in 5.8s ===============================
```

---

## 6. Financial Logic & Calculations

1. **Current Net Balance (All-Time):**
   $$\text{Balance} = \sum(\text{All User Incomes}) - \sum(\text{All User Expenses})$$
2. **Monthly Net Savings:**
   $$\text{Savings}_{\text{Month}} = \text{Income}_{\text{Month}} - \text{Expenses}_{\text{Month}}$$
3. **Savings Rate (%):**
   $$\text{Savings Rate} = \left(\frac{\text{Savings}_{\text{Month}}}{\text{Income}_{\text{Month}}}\right) \times 100 \quad (\text{if Income} > 0, \text{ else } 0\%)$$
4. **Remaining Budget per Category:**
   $$\text{Remaining} = \text{Monthly Limit} - \sum(\text{Category Expenses in that Month})$$
5. **Threshold Status Engine:**
   - $\text{Usage} < 80\% \rightarrow \text{Healthy (Green/Teal)}$
   - $80\% \le \text{Usage} \le 100\% \rightarrow \text{Warning (Amber Banner)}$
   - $\text{Usage} > 100\% \rightarrow \text{Exceeded Alert (Rose Alert Banner)}$

---

## 7. Security Architecture & Data Isolation

1. **Password Hashing:**
   Utilizes `werkzeug.security.generate_password_hash()` implementing cryptographically secure `scrypt` hashing. Plaintext passwords are never stored or logged.
2. **Per-User Query Isolation:**
   Every single transaction, budget, report calculation, and CSV export strictly filters on `Transaction.user_id == current_user.id` or uses `Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()`. A user cannot view, edit, or delete another user's financial data even by manually guessing URL IDs (returns HTTP 404).
3. **CSRF Protection:**
   All HTML forms are protected against Cross-Site Request Forgery via `Flask-WTF` and WTForms token injection.
4. **Open-Redirect Defense:**
   The `next` URL parameter during login is validated via `urlsplit(next_page).netloc == ''` to prevent malicious off-site redirects.

---

## 8. Deployment Guide (Production)

### Deploying to Render.com (Recommended Free Hosting)
1. Push the code repository to **GitHub**.
2. Log into [Render.com](https://render.com) and click **New + > Web Service**.
3. Connect your GitHub repository.
4. Select **Python 3** environment.
5. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app` (or `python run.py`)
6. Under **Environment Variables**, add:
   - `SECRET_KEY`: A strong random string (e.g. generated via `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV`: `production`

---

## 9. College Presentation Script & Demo Guide

When demonstrating ALTO to professors, evaluators, or interviewers:

1. **The Problem:** *"Most budgeting apps are either bloated with ads or store sensitive personal numbers on untrusted third-party services. ALTO solves this by providing a clean, distraction-free, self-hosted personal finance platform."*
2. **The Architecture:** *"I structured ALTO using Flask's Application Factory pattern and modular Blueprints (`auth`, `dashboard`, `transactions`, `budgets`, `reports`, `profile`). This enforces separation of concerns and maintainability."*
3. **Live Demonstration:**
   - Sign in with `demo@alto.app` / `alto1234`.
   - Point out the real-time calculated KPI cards and the Chart.js 6-month comparative cash flow chart.
   - Demonstrate the Budget Tracker: highlight how the Entertainment category triggered an **Exceeded Alert** and Dining Out triggered an **80% Caution Alert**.
   - Navigate to Transactions: show live keyword search, type filter (Income vs Expense), and sorting.
   - Add a transaction: observe the vanilla JavaScript dynamic category dropdown change based on Income vs Expense.
   - Go to Reports: show the period presets, payment distribution chart, and demonstrate the **Export CSV** download.
   - Switch currency to **$ USD** in Profile & Settings and show that all symbols across the site immediately update.
4. **Engineering Rigor:** *"The application includes 19 automated pytest tests covering user authentication, financial calculations, threshold warnings, and user data isolation."*

---

## 10. Resume-Ready Project Description

**ALTO – Full-Stack Personal Finance Tracker Web Application**  
*Python, Flask, SQLAlchemy, SQLite, Chart.js, HTML5/CSS3, Vanilla JavaScript, Pytest*
- Architected and built a responsive full-stack finance tracking web application using Flask Blueprints, SQLAlchemy ORM, and SQLite.
- Implemented real-time financial algorithms to compute all-time net balances, monthly cash flow, savings rates, and category budget health.
- Designed an interactive SaaS UI using vanilla JavaScript and Chart.js for 6-month cash flow trends and category expense distributions.
- Engineered monthly budget tracking with automated threshold warnings (80% caution, >100% exceeded alert banners).
- Enforced enterprise security best practices: scrypt password hashing, CSRF form protection, and strict per-user query isolation.
- Built a 19-test automated test suite with pytest covering authentication, CRUD operations, budget calculations, and security isolation.
