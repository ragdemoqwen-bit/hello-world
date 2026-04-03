"""
Employment & Income Verification Integration

External Dependency: Employment Verification Service (e.g., Plaid, The Work Number / Equifax Workforce Solutions)
-----------------------------------------------------------------------------------------------------------------
In production, this module connects to employment/income verification
services to confirm borrower employment status and income.

Required Configuration:
    - EMPLOYMENT_VERIFY_API_KEY: API key for the verification service
    - EMPLOYMENT_VERIFY_API_URL: Base URL
    - PLAID_CLIENT_ID: (if using Plaid) Client ID
    - PLAID_SECRET: (if using Plaid) Secret key

API Contract (Plaid-style):
    POST /v1/income/verification
    Request:
        {
            "employer_name": "Acme Corp",
            "employee_first_name": "John",
            "employee_last_name": "Doe",
            "ssn_last_four": "1234",
            "stated_income": 85000.00
        }
    Response:
        {
            "verification_id": "empv_abc123",
            "status": "verified",
            "employer_name": "Acme Corp",
            "employer_verified": true,
            "employment_status": "active",
            "start_date": "2020-03-15",
            "job_title": "Software Engineer",
            "income_verified": true,
            "verified_annual_income": 87500.00,
            "pay_frequency": "bi-weekly",
            "last_pay_date": "2024-01-12",
            "ytd_gross_income": 3365.38,
            "confidence_score": 0.95
        }

API Contract (The Work Number-style):
    POST /v1/verifications/employment
    Request:
        {
            "subject": {
                "ssn": "XXX-XX-1234",
                "first_name": "John",
                "last_name": "Doe"
            },
            "purpose": "mortgage_lending"
        }
    Response:
        {
            "employer": "Acme Corp",
            "status": "currently_employed",
            "original_hire_date": "2020-03-15",
            "most_recent_hire_date": "2020-03-15",
            "job_title": "Software Engineer",
            "rate_of_pay": 87500.00,
            "pay_frequency": "bi-weekly",
            "average_hours": 40
        }
"""

import random
from dataclasses import dataclass


@dataclass
class EmploymentVerificationResult:
    verification_id: str
    status: str
    employer_verified: bool
    employment_status: str
    verified_annual_income: float
    income_verified: bool
    confidence_score: float
    job_title: str | None = None


class EmploymentVerificationClient:
    """
    Client for Employment/Income Verification APIs.

    In production, replace simulate methods with actual Plaid
    or Work Number API calls.
    """

    def __init__(self, api_key: str | None = None, api_url: str | None = None):
        self.api_key = api_key
        self.api_url = api_url or "https://api.employment-verify.example.com/v1"

    def verify_employment(
        self,
        employer_name: str | None,
        first_name: str,
        last_name: str,
        ssn_last_four: str,
        stated_income: float,
    ) -> EmploymentVerificationResult:
        """
        Verify employment and income for a borrower.

        In production, this calls the employment verification API.
        """
        return self._simulate_employment_check(stated_income, ssn_last_four)

    def _simulate_employment_check(
        self, stated_income: float, ssn_last_four: str
    ) -> EmploymentVerificationResult:
        """Generate simulated employment verification results."""
        seed = int(ssn_last_four) if ssn_last_four.isdigit() else 5000
        rng = random.Random(seed + 200)

        employed = rng.random() > 0.05
        income_variance = rng.uniform(-0.1, 0.15)
        verified_income = stated_income * (1 + income_variance)

        return EmploymentVerificationResult(
            verification_id=f"empv_{rng.randint(100000, 999999)}",
            status="verified" if employed else "unable_to_verify",
            employer_verified=employed,
            employment_status="active" if employed else "unknown",
            verified_annual_income=round(verified_income, 2),
            income_verified=employed and abs(income_variance) < 0.2,
            confidence_score=round(rng.uniform(0.85, 0.99), 2) if employed else round(rng.uniform(0.1, 0.4), 2),
            job_title="Verified Position" if employed else None,
        )


employment_verification_client = EmploymentVerificationClient()
