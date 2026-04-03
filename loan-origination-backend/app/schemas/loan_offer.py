from datetime import datetime

from pydantic import BaseModel


class LoanOfferResponse(BaseModel):
    id: str
    application_id: str
    approved_amount: float
    interest_rate: float
    loan_term_months: int
    monthly_payment: float
    apr: float
    origination_fee: float
    total_interest: float
    total_cost: float
    requires_collateral: bool
    status: str
    expires_at: datetime | None = None
    created_at: datetime
    accepted_at: datetime | None = None

    model_config = {"from_attributes": True}


class LoanOfferAccept(BaseModel):
    accepted: bool
