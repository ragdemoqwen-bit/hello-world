from datetime import datetime

from pydantic import BaseModel

from app.schemas.borrower import BorrowerCreate, BorrowerResponse


class LoanApplicationCreate(BaseModel):
    borrower: BorrowerCreate
    loan_type: str
    requested_amount: float
    loan_purpose: str
    loan_term_months: int = 360
    property_address: str | None = None
    property_value: float | None = None
    vehicle_info: str | None = None


class LoanApplicationResponse(BaseModel):
    id: str
    borrower_id: str
    loan_type: str
    requested_amount: float
    loan_purpose: str
    loan_term_months: int
    property_address: str | None = None
    property_value: float | None = None
    vehicle_info: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    borrower: BorrowerResponse | None = None

    model_config = {"from_attributes": True}


class LoanApplicationSummary(BaseModel):
    id: str
    borrower_name: str
    loan_type: str
    requested_amount: float
    status: str
    created_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: str | None = None
    changed_by: str = "system"
