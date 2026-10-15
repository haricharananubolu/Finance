"""
Generates an executive, professional PDF Project Solution Document for ALTO.
Contains the live Render URL (https://finance-g9aj.onrender.com), GitHub repo,
system architecture, problem statement, core algorithms, and testing results.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_filename = "ALTO_Project_Solution_Document.pdf"
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom styles
primary_color = colors.HexColor("#0284c7")
dark_navy = colors.HexColor("#0f172a")
light_slate = colors.HexColor("#f8fafc")
border_color = colors.HexColor("#cbd5e1")

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=dark_navy,
    spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=14,
    textColor=primary_color,
    spaceAfter=10
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=dark_navy,
    spaceBefore=10,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor("#334155"),
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'BulletText',
    parent=body_style,
    leftIndent=14,
    firstLineIndent=-10,
    spaceAfter=3
)

link_style = ParagraphStyle(
    'LinkText',
    parent=body_style,
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#0284c7")
)

story = []

# Title & Subtitle
story.append(Paragraph("ALTO — Personal Finance Tracker", title_style))
story.append(Paragraph("PROJECT SOLUTION & SYSTEM DESIGN SPECIFICATION", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

# Live Links Banner Box
links_data = [
    [
        Paragraph("<b>🌐 Live Deployed Application:</b><br/><font color='#0284c7'><u>https://finance-g9aj.onrender.com</u></font>", body_style),
        Paragraph("<b>💻 GitHub Source Repository:</b><br/><font color='#0284c7'><u>https://github.com/haricharananubolu/Finance</u></font>", body_style)
    ],
    [
        Paragraph("<b>🔑 Demo Account:</b> demo@alto.app", body_style),
        Paragraph("<b>🔒 Demo Password:</b> alto1234 (Pre-seeded with 22 transactions & 7 budgets)", body_style)
    ]
]
links_table = Table(links_data, colWidths=[270, 270])
links_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), light_slate),
    ('BOX', (0, 0), (-1, -1), 1, border_color),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
]))
story.append(links_table)
story.append(Spacer(1, 10))

# 1. Problem Statement & Solution
story.append(Paragraph("1. Executive Summary & Problem Statement", h2_style))
story.append(Paragraph(
    "<b>The Problem:</b> Individuals make poor financial choices because traditional tools provide passive post-mortem data rather than proactive, real-time threshold warnings before critical budget overspending occurs. Modern users managing high-velocity digital payments (UPI, Cards, Net Banking) struggle with unmonitored cash leaks and lack actionable clarity into savings velocity.",
    body_style
))
story.append(Paragraph(
    "<b>The Solution:</b> <i>ALTO</i> is a full-stack personal finance management web application built with Python (Flask), SQLAlchemy ORM, SQLite, and Vanilla JavaScript. It delivers real-time net cash flow calculations, automated category budget health tracking (with predictive 80% caution and 100% cap breach alerts), interactive Chart.js visualizations, and strict per-user database isolation without intrusive third-party data tracking.",
    body_style
))

# 2. Technology Stack & Architecture
story.append(Paragraph("2. System Architecture & Technology Stack", h2_style))
tech_data = [
    [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Role & Technical Highlights</b>", body_style)],
    [Paragraph("Backend", body_style), Paragraph("Python 3.12, Flask 3.0", body_style), Paragraph("Application Factory pattern with modular Blueprints (auth, dashboard, transactions, budgets, reports).", body_style)],
    [Paragraph("Database", body_style), Paragraph("SQLite, SQLAlchemy 2.0", body_style), Paragraph("ACID relational schema with fixed-point Decimal representation to eliminate monetary rounding errors.", body_style)],
    [Paragraph("Security", body_style), Paragraph("Flask-Login, Flask-WTF", body_style), Paragraph("Cryptographically secure Scrypt password hashing, CSRF tokens on all POST endpoints, and strict query isolation.", body_style)],
    [Paragraph("Frontend", body_style), Paragraph("HTML5, CSS3, Vanilla JS", body_style), Paragraph("Custom SaaS design system, responsive mobile drawer, and Chart.js 6-month comparative cash flow bar & doughnut charts.", body_style)],
    [Paragraph("Testing", body_style), Paragraph("Pytest 8.2 (19 Tests)", body_style), Paragraph("100% automated test coverage across authentication, CRUD workflows, budget health thresholds, and security isolation.", body_style)],
    [Paragraph("Hosting", body_style), Paragraph("Render Cloud, Gunicorn", body_style), Paragraph("Production WSGI deployment with zero-downtime continuous deployment from GitHub main branch.", body_style)]
]
tech_table = Table(tech_data, colWidths=[70, 130, 340])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
    ('BOX', (0, 0), (-1, -1), 1, border_color),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
]))
story.append(tech_table)

# 3. Core Algorithms & Logic
story.append(Paragraph("3. Core Mathematical Algorithms & Budget Alert Engine", h2_style))
story.append(Paragraph("• <b>All-Time Net Balance:</b> Computed dynamically via <code>&sum;(Recorded Incomes) &minus; &sum;(Recorded Expenses)</code>.", bullet_style))
story.append(Paragraph("• <b>Monthly Savings Rate (%):</b> <code>((Income - Expenses) / Income) &times; 100</code> when Income > 0, tracking wealth accumulation pace.", bullet_style))
story.append(Paragraph("• <b>Automated Budget Thresholds:</b> Category limits automatically evaluate consumption against live expense entries:", bullet_style))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&bull; <b>Healthy Status (&lt; 80% limit):</b> Normal spending trajectory with teal indicators.", bullet_style))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&bull; <b>Caution Status (80% &ndash; 100% limit):</b> Triggers amber warning banner before financial breach.", bullet_style))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&bull; <b>Exceeded Status (&gt; 100% limit):</b> Triggers high-priority rose alert banner indicating overspending.", bullet_style))

# 4. Key Functional Features
story.append(Paragraph("4. Key Functional Modules", h2_style))
story.append(Paragraph("• <b>Real-Time Financial Dashboard:</b> Instant KPI cards, 6-month cash flow trends, category doughnut chart, and recent transaction feeds.", bullet_style))
story.append(Paragraph("• <b>Transaction Manager:</b> Full CRUD workflows with search, multi-criteria filtering, sorting, pagination, and dynamic category dropdowns.", bullet_style))
story.append(Paragraph("• <b>Monthly Budget Planner:</b> Target limit assignment per category with real-time visual progress meters reflecting actual expenses.", bullet_style))
story.append(Paragraph("• <b>Reports & CSV Export:</b> Flexible period presets (This Month, Last Month, This Year, All Time) with one-click RFC-4180 CSV spreadsheet export.", bullet_style))
story.append(Paragraph("• <b>User Preferences:</b> Multi-currency support (default &#8377; INR, $, &euro;, &pound;, &yen;, AED) and secure in-app password changes.", bullet_style))

# 5. Verification & Live URL Access
story.append(Paragraph("5. Live Deployment & Evaluation Access", h2_style))
story.append(Paragraph(
    "The application is fully operational in production. Evaluators can access the live service directly at <b><u>https://finance-g9aj.onrender.com</u></b> using the demo credentials provided above or by creating a new account via the registration portal.",
    body_style
))

story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=8, spaceAfter=6))
story.append(Paragraph("<i>ALTO Personal Finance Tracker &bull; Full-Stack Capstone Project &bull; Live URL: https://finance-g9aj.onrender.com</i>", ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

doc.build(story)
print(f"Successfully generated {pdf_filename} (Size: {os.path.getsize(pdf_filename)} bytes)")
