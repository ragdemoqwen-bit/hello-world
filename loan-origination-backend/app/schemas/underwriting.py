from datetime import datetime

from pydantic import BaseModel


class UnderwritingResultResponse(BaseModel):
    id: str
    application_id: str
    credit_score: int
    dti_ratio: float
    ltv_ratio: float | None = None
    risk_score: float
    risk_level: str
    decision: str
    conditions: str | None = None
    denial_reasons: str | None = None
    notes: str | None = None
    decided_at: datetime

    model_config = {"from_attributes": True}
