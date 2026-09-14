from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import List
from ..database import get_db
from ..models.budget import Budget
from ..models.category import Category
from ..models.transaction import Transaction, TransactionType
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

class BudgetCreate(BaseModel):
    category_id: int
    amount: float
    month: int
    year: int

class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float
    spent: float
    remaining: float
    percentage: float
    month: int
    year: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == budget_data.category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_data.category_id,
        Budget.month == budget_data.month,
        Budget.year == budget_data.year
    ).first()
    
    if existing:
        existing.amount = budget_data.amount
        db.commit()
        db.refresh(existing)
        budget = existing
    else:
        budget = Budget(
            user_id=current_user.id,
            category_id=budget_data.category_id,
            amount=budget_data.amount,
            month=budget_data.month,
            year=budget_data.year
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
    
    spent = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == budget_data.category_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.date >= date(budget_data.year, budget_data.month, 1)
    ).all()
    total_spent = sum(t.amount for t in spent)
    
    return {
        "id": budget.id,
        "category": category.name,
        "amount": budget.amount,
        "spent": total_spent,
        "remaining": max(0, budget.amount - total_spent),
        "percentage": (total_spent / budget.amount * 100) if budget.amount > 0 else 0,
        "month": budget.month,
        "year": budget.year
    }

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    month: int,
    year: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == month,
        Budget.year == year
    ).all()
    
    result = []
    for budget in budgets:
        category = db.query(Category).filter(Category.id == budget.category_id).first()
        if not category:
            continue
        
        spent = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == budget.category_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= date(year, month, 1)
        ).all()
        total_spent = sum(t.amount for t in spent)
        
        result.append({
            "id": budget.id,
            "category": category.name,
            "amount": budget.amount,
            "spent": total_spent,
            "remaining": max(0, budget.amount - total_spent),
            "percentage": (total_spent / budget.amount * 100) if budget.amount > 0 else 0,
            "month": budget.month,
            "year": budget.year
        })
    
    return result
