from datetime import datetime

from pydantic import BaseModel, EmailStr


class BorrowerCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: str
    ssn_last_four: str
    address_street: str
    address_city: str
    address_state: str
    address_zip: str
    employer_name: str | None = None
    job_title: str | None = None
    employment_years: float | None = None
    annual_income: float
    monthly_debt_payments: float = 0.0


class BorrowerResponse(BorrowerCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
