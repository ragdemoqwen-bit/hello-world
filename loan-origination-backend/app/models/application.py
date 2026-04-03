import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LoanType(str, PyEnum):
    PERSONAL = "personal"
    MORTGAGE = "mortgage"
    AUTO = "auto"
    BUSINESS = "business"
    STUDENT = "student"


class ApplicationStatus(str, PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    DOCUMENTS_PENDING = "documents_pending"
    CREDIT_CHECK = "credit_check"
    KYC_VERIFICATION = "kyc_verification"
    EMPLOYMENT_VERIFICATION = "employment_verification"
    APPRAISAL = "appraisal"
    UNDERWRITING = "underwriting"
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    DENIED = "denied"
    LOAN_OFFERED = "loan_offered"
    OFFER_ACCEPTED = "offer_accepted"
    CLOSING = "closing"
    FUNDED = "funded"
    WITHDRAWN = "withdrawn"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    borrower_id: Mapped[str] = mapped_column(String, ForeignKey("borrowers.id"))
    loan_type: Mapped[str] = mapped_column(Enum(LoanType))
    requested_amount: Mapped[float] = mapped_column(Float)
    loan_purpose: Mapped[str] = mapped_column(String(255))
    loan_term_months: Mapped[int] = mapped_column(default=360)
    property_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    property_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    vehicle_info: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    borrower: Mapped["Borrower"] = relationship(back_populates="applications")
    documents: Mapped[list["Document"]] = relationship(back_populates="application")
    credit_report: Mapped["CreditReport | None"] = relationship(back_populates="application", uselist=False)
    underwriting_result: Mapped["UnderwritingResult | None"] = relationship(back_populates="application", uselist=False)
    loan_offer: Mapped["LoanOffer | None"] = relationship(back_populates="application", uselist=False)
    status_history: Mapped[list["StatusHistory"]] = relationship(back_populates="application")
