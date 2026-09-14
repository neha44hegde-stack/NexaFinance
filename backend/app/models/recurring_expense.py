from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class FrequencyType(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    frequency = Column(Enum(FrequencyType), nullable=False)
    next_due_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="recurring_expenses")
    category = relationship("Category")