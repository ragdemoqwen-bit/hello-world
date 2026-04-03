from datetime import datetime

from pydantic import BaseModel


class CreditReportResponse(BaseModel):
    id: str
    application_id: str
    bureau: str
    credit_score: int
    total_accounts: int | None = None
    open_accounts: int | None = None
    delinquent_accounts: int | None = None
    total_balance: float | None = None
    monthly_payments: float | None = None
    bankruptcies: int = 0
    collections: int = 0
    hard_inquiries_last_12m: int = 0
    pulled_at: datetime

    model_config = {"from_attributes": True}
