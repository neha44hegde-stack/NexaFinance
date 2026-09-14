# backend/services.py

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from backend.models import User, Transaction, Budget, SavingsGoal, RecurringExpense, Subscription
from backend.schemas import (
    TransactionCreate, BudgetCreate, SavingsGoalCreate, 
    RecurringExpenseCreate, SubscriptionCreate
)
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from collections import defaultdict

class FinanceService:
    
    @staticmethod
    def get_user_transactions(db: Session, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        return query.order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def get_current_balance(db: Session, user_id: int) -> float:
        """Calculate current balance (total income - total expenses)"""
        transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expenses = sum(t.amount for t in transactions if t.type == "expense")
        return total_income - total_expenses
    
    @staticmethod
    def get_monthly_spending(db: Session, user_id: int, month: int, year: int) -> Dict[str, float]:
        """Get spending breakdown by category for a specific month"""
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= date(year, month, 1),
            Transaction.date <= date(year, month, 28)
        ).all()
        
        category_spending = defaultdict(float)
        for t in transactions:
            category_spending[t.category] += t.amount
        return dict(category_spending)
    
    @staticmethod
    def get_savings_goals(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get all savings goals with progress"""
        goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
        result = []
        for goal in goals:
            progress = (goal.saved_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            days_left = (goal.deadline - date.today()).days if goal.deadline else None
            result.append({
                "id": goal.id,
                "name": goal.name,
                "target": goal.target_amount,
                "saved": goal.saved_amount,
                "progress": min(progress, 100),
                "deadline": goal.deadline,
                "days_left": days_left
            })
        return result
    
    @staticmethod
    def generate_financial_insights(db: Session, user_id: int) -> List[Dict[str, str]]:
        """Generate rule-based financial insights from actual data"""
        insights = []
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        # Get current month's spending
        current_spending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= date(current_year, current_month, 1),
            Transaction.date <= today
        ).all()
        
        total_current_spending = sum(t.amount for t in current_spending)
        
        # Get previous month's spending
        if current_month == 1:
            prev_month, prev_year = 12, current_year - 1
        else:
            prev_month, prev_year = current_month - 1, current_year
            
        prev_spending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= date(prev_year, prev_month, 1),
            Transaction.date <= date(prev_year, prev_month, 28)
        ).all()
        
        total_prev_spending = sum(t.amount for t in prev_spending)
        
        # Insight 1: Compare with last month
        if total_prev_spending > 0:
            percent_change = ((total_current_spending - total_prev_spending) / total_prev_spending) * 100
            if percent_change > 10:
                insights.append({
                    "type": "spending_increase",
                    "message": f"Your spending is {percent_change:.1f}% higher than last month.",
                    "severity": "warning"
                })
            elif percent_change < -10:
                insights.append({
                    "type": "spending_decrease",
                    "message": f"Your spending has decreased by {abs(percent_change):.1f}% compared with last month.",
                    "severity": "success"
                })
        
        # Insight 2: Category breakdown
        if current_spending:
            category_spending = defaultdict(float)
            for t in current_spending:
                category_spending[t.category] += t.amount
            
            if category_spending:
                top_category = max(category_spending, key=category_spending.get)
                top_percentage = (category_spending[top_category] / total_current_spending) * 100
                if top_percentage > 25:
                    insights.append({
                        "type": "category_breakdown",
                        "message": f"{top_category} accounts for {top_percentage:.1f}% of your spending this month.",
                        "severity": "info"
                    })
        
        # Insight 3: Budget check
        budgets = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == current_month,
            Budget.year == current_year
        ).all()
        
        for budget in budgets:
            category_spending = sum(
                t.amount for t in current_spending 
                if t.category == budget.category
            )
            if category_spending > budget.amount * 0.9:
                remaining = budget.amount - category_spending
                insights.append({
                    "type": "budget_warning",
                    "message": f"You're close to exceeding your monthly budget for {budget.category}. Remaining: {remaining:.2f}",
                    "severity": "danger"
                })
        
        return insights
    
    @staticmethod
    def forecast_expenses(db: Session, user_id: int, months_ahead: int = 1) -> Dict[str, Any]:
        """Forecast future expenses using Scikit-learn when enough data exists"""
        today = date.today()
        start_date = date(today.year - 1, today.month, 1)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date
        ).all()
        
        if len(transactions) < 3:
            return {
                "available": False,
                "message": "Not enough historical data to generate a forecast."
            }
        
        monthly_totals = defaultdict(float)
        for t in transactions:
            key = (t.date.year, t.date.month)
            monthly_totals[key] += t.amount
        
        months = sorted(monthly_totals.keys())
        
        if len(months) < 3:
            return {
                "available": False,
                "message": "Not enough historical data to generate a forecast. Need at least 3 months of data."
            }
        
        X = np.array(range(len(months))).reshape(-1, 1)
        y = np.array([monthly_totals[m] for m in months])
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_idx = len(months) - 1
        forecast_values = []
        for i in range(1, months_ahead + 1):
            pred = model.predict([[last_idx + i]])[0]
            forecast_values.append(max(0, pred))
        
        return {
            "available": True,
            "historical_data": [{"month": f"{m[0]}-{m[1]:02d}", "amount": monthly_totals[m]} for m in months],
            "forecast": [{"month": f"{future_year}-{future_month:02d}", "amount": val} 
                        for val, (future_year, future_month) in zip(forecast_values, 
                        [(today.year + (today.month + i - 1) // 12, (today.month + i - 1) % 12 + 1) 
                         for i in range(1, months_ahead + 1)])]
        }
    
    @staticmethod
    def can_afford_purchase(db: Session, user_id: int, purchase_name: str, purchase_amount: float) -> Dict[str, Any]:
        """Check if user can afford a purchase based on balance, budget, and savings goals"""
        balance = FinanceService.get_current_balance(db, user_id)
        
        today = date.today()
        monthly_budgets = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == today.month,
            Budget.year == today.year
        ).all()
        
        total_budget = sum(b.amount for b in monthly_budgets) if monthly_budgets else 0
        current_spending = sum(
            t.amount for t in db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.date >= date(today.year, today.month, 1)
            ).all()
        )
        remaining_budget = total_budget - current_spending if total_budget > 0 else float('inf')
        
        savings_goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
        total_savings_goal = sum(g.target_amount - g.saved_amount for g in savings_goals)
        
        result = {
            "purchase": purchase_name,
            "amount": purchase_amount,
            "can_afford": purchase_amount <= (balance - total_savings_goal),
            "balance": balance,
            "remaining_budget": remaining_budget,
            "savings_shortfall": total_savings_goal,
            "details": []
        }
        
        if balance < purchase_amount:
            result["details"].append(f"❌ Insufficient balance. Need ${purchase_amount - balance:.2f} more.")
        else:
            result["details"].append(f"✅ You have enough balance (${balance:.2f})")
        
        if remaining_budget != float('inf') and remaining_budget < purchase_amount:
            result["details"].append(f"⚠️ This exceeds your remaining monthly budget by ${purchase_amount - remaining_budget:.2f}")
        elif remaining_budget != float('inf'):
            result["details"].append(f"✅ Within your monthly budget (${remaining_budget:.2f} remaining)")
        
        if total_savings_goal > 0:
            if purchase_amount > total_savings_goal:
                result["details"].append(f"⚠️ This would reduce your savings goals by ${purchase_amount:.2f}")
            else:
                result["details"].append(f"✅ Your savings goals remain protected")
        
        if result["can_afford"]:
            result["details"].append("✅ You can afford this purchase!")
        else:
            result["details"].append("❌ You cannot afford this purchase right now.")
        
        return result