from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Index, CheckConstraint, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(30), default="Cash", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="expenses")

    __table_args__ = (
        Index("idx_user_expense_date_cat", "user_id", "date", "category"),
        CheckConstraint("amount > 0", name="check_positive_expense_amount"),
    )
