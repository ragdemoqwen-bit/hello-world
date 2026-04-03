import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentType(str, PyEnum):
    PAY_STUB = "pay_stub"
    W2 = "w2"
    TAX_RETURN = "tax_return"
    BANK_STATEMENT = "bank_statement"
    ID_DOCUMENT = "id_document"
    PROOF_OF_ADDRESS = "proof_of_address"
    EMPLOYMENT_LETTER = "employment_letter"
    PROPERTY_APPRAISAL = "property_appraisal"
    TITLE_REPORT = "title_report"
    INSURANCE_PROOF = "insurance_proof"
    OTHER = "other"


class DocumentStatus(str, PyEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String, ForeignKey("loan_applications.id"))
    document_type: Mapped[str] = mapped_column(Enum(DocumentType))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    application: Mapped["LoanApplication"] = relationship(back_populates="documents")
