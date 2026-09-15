# NexaFinance - Full-Stack Personal Finance Tracker

A complete personal finance management web application with secure authentication.

## Live Demo
- App: https://nexafinance-1.onrender.com

## Features
- Income and Expense Tracking (Full CRUD)
- Budgets with real-time over-budget alerts
- Savings Goals with progress tracking
- Loans with Pay EMI feature
- Recurring Expenses (auto-added monthly)
- Assets and Net Worth tracker
- "Can I Afford It?" calculator
- Indian Tax Estimator (AY 2025-26)
- Interactive charts (Bar, Doughnut, Line)
- Light/Dark mode with CSV export

## Tech Stack

Frontend:
- HTML5, CSS3, Vanilla JavaScript
- Chart.js for data visualization

Backend:
- Python, Flask (REST API)
- SQLAlchemy (ORM)
- Flask-JWT-Extended (Authentication)
- Werkzeug (Password Hashing)

Database:
- PostgreSQL (Production)
- SQLite (Local Development)

Deployment:
- Render

## Project Structure

    NexaFinance/
    |-- backend/
    |   |-- app.py
    |   |-- requirements.txt
    |   |-- Procfile
    |   |-- index.html
    |-- expense-tracker/
    |   |-- index.html
    |-- README.md

## Local Setup

1. Clone the repository:
    git clone https://github.com/neha44hegde-stack/NexaFinance.git
    cd NexaFinance

2. Backend setup:
    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

3. Frontend:
    Open expense-tracker/index.html in your browser.

## Author

Neha Hegde
- GitHub: https://github.com/neha44hegde-stack
