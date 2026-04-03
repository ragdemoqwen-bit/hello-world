import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UnderwritingDecision(str, PyEnum):
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    DENIED = "denied"
    MANUAL_REVIEW = "manual_review"


class RiskLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UnderwritingResult(Base):
    __tablename__ = "underwriting_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("loan_applications.id"), unique=True)
    credit_score: Mapped[int] = mapped_column()
    dti_ratio: Mapped[float] = mapped_column(Float)
    ltv_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(Enum(RiskLevel))
    decision: Mapped[str] = mapped_column(Enum(UnderwritingDecision))
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    denial_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["LoanApplication"] = relationship(back_populates="underwriting_result")
