import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OfferStatus(str, PyEnum):
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    COUNTERED = "countered"


class LoanOffer(Base):
    __tablename__ = "loan_offers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("loan_applications.id"), unique=True)
    approved_amount: Mapped[float] = mapped_column(Float)
    interest_rate: Mapped[float] = mapped_column(Float)
    loan_term_months: Mapped[int] = mapped_column(Integer)
    monthly_payment: Mapped[float] = mapped_column(Float)
    apr: Mapped[float] = mapped_column(Float)
    origination_fee: Mapped[float] = mapped_column(Float, default=0.0)
    total_interest: Mapped[float] = mapped_column(Float)
    total_cost: Mapped[float] = mapped_column(Float)
    requires_collateral: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(Enum(OfferStatus), default=OfferStatus.PENDING)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    application: Mapped["LoanApplication"] = relationship(back_populates="loan_offer")
