import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CreditReport(Base):
    __tablename__ = "credit_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("loan_applications.id"), unique=True)
    bureau: Mapped[str] = mapped_column(String(50))
    credit_score: Mapped[int] = mapped_column(Integer)
    total_accounts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_accounts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delinquent_accounts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_payments: Mapped[float | None] = mapped_column(Float, nullable=True)
    bankruptcies: Mapped[int] = mapped_column(Integer, default=0)
    collections: Mapped[int] = mapped_column(Integer, default=0)
    hard_inquiries_last_12m: Mapped[int] = mapped_column(Integer, default=0)
    report_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    pulled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["LoanApplication"] = relationship(back_populates="credit_report")
