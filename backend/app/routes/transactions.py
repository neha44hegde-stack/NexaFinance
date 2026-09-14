from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from ..database import get_db
from ..models.transaction import Transaction, TransactionType
from ..models.category import Category
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    category_name: Optional[str] = None
    description: Optional[str] = None
    date: date

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    category: Optional[str]
    description: Optional[str]
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = None
    if transaction.category_name:
        category = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.name == transaction.category_name
        ).first()
        
        if not category:
            category = Category(
                user_id=current_user.id,
                name=transaction.category_name,
                type=transaction.type
            )
            db.add(category)
            db.flush()
    
    new_transaction = Transaction(
        user_id=current_user.id,
        type=transaction.type,
        amount=transaction.amount,
        category_id=category.id if category else None,
        description=transaction.description,
        date=transaction.date
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {
        "id": new_transaction.id,
        "user_id": new_transaction.user_id,
        "type": new_transaction.type,
        "amount": new_transaction.amount,
        "category": transaction.category_name,
        "description": new_transaction.description,
        "date": new_transaction.date,
        "created_at": new_transaction.created_at
    }

@router.get("/")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return transactions

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
    balance = total_income - total_expenses
    
    return {
        "balance": balance,
        "income": total_income,
        "expenses": total_expenses
    }
