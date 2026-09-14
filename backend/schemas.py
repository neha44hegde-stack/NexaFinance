# backend/schemas.py

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# ============ USER SCHEMAS ============

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

# ============ TRANSACTION SCHEMAS ============

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    date: Optional[date] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    category: str
    description: Optional[str]
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ BUDGET SCHEMAS ============

class BudgetCreate(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    month: int
    year: int
    spent: Optional[float] = 0
    remaining: Optional[float] = 0
    
    class Config:
        from_attributes = True

# ============ SAVINGS GOAL SCHEMAS ============

class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    saved_amount: Optional[float] = Field(0, ge=0)
    deadline: Optional[date] = None

class SavingsGoalResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    saved_amount: float
    progress: float
    deadline: Optional[date]
    days_left: Optional[int]
    
    class Config:
        from_attributes = True

# ============ RECURRING EXPENSE SCHEMAS ============

class FrequencyType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurringExpenseCreate(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    frequency: FrequencyType
    category: Optional[str] = None
    next_due_date: date

class RecurringExpenseResponse(BaseModel):
    id: int
    name: str
    amount: float
    frequency: str
    category: Optional[str]
    next_due_date: date
    active: bool
    
    class Config:
        from_attributes = True

# ============ SUBSCRIPTION SCHEMAS ============

class SubscriptionCreate(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    billing_cycle: str  # "monthly" or "yearly"
    next_billing_date: date
    category: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: int
    name: str
    amount: float
    billing_cycle: str
    next_billing_date: date
    category: Optional[str]
    active: bool
    monthly_cost: float
    annual_cost: float
    
    class Config:
        from_attributes = True

# ============ SETTINGS SCHEMAS ============

class SettingsUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    currency: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None

# ============ REPORT SCHEMAS ============

class MonthlyReport(BaseModel):
    month: int
    year: int
    total_income: float
    total_expenses: float
    balance: float
    savings: float
    savings_rate: float
    top_spending_category: Optional[str]
    largest_expense: Optional[Dict[str, Any]]
    average_daily_spending: float
    budget_status: Dict[str, Any]
    subscriptions: List[Dict[str, Any]]

# ============ INSIGHT SCHEMAS ============

class InsightResponse(BaseModel):
    type: str
    message: str
    severity: str  # "info", "warning", "danger", "success"

# ============ FORECAST SCHEMAS ============

class ForecastResponse(BaseModel):
    available: bool
    message: Optional[str] = None
    historical_data: Optional[List[Dict[str, Any]]] = None
    forecast: Optional[List[Dict[str, Any]]] = None

# ============ CAN AFFORD SCHEMAS ============

class CanAffordRequest(BaseModel):
    purchase_name: str
    purchase_amount: float = Field(..., gt=0)

class CanAffordResponse(BaseModel):
    purchase: str
    amount: float
    can_afford: bool
    balance: float
    remaining_budget: float
    savings_shortfall: float
    details: List[str]
