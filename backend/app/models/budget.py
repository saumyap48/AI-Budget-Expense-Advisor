from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, UniqueConstraint, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_budget = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "month", "year", name="uq_user_budget_month_year"),
        CheckConstraint("monthly_budget > 0", name="check_positive_monthly_budget"),
        CheckConstraint("month BETWEEN 1 AND 12", name="check_valid_month"),
    )
