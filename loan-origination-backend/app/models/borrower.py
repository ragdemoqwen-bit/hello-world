import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Borrower(Base):
    __tablename__ = "borrowers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    date_of_birth: Mapped[str] = mapped_column(String(10))
    ssn_last_four: Mapped[str] = mapped_column(String(4))
    address_street: Mapped[str] = mapped_column(String(255))
    address_city: Mapped[str] = mapped_column(String(100))
    address_state: Mapped[str] = mapped_column(String(2))
    address_zip: Mapped[str] = mapped_column(String(10))
    employer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_income: Mapped[float] = mapped_column(Float)
    monthly_debt_payments: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications: Mapped[list["LoanApplication"]] = relationship(back_populates="borrower")
