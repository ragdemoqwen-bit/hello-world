"""
Credit Bureau Integration Interface

External Dependency: Credit Bureau API (Equifax, Experian, TransUnion)
----------------------------------------------------------------------
In production, this module would integrate with one or more credit bureaus
to pull credit reports and scores for loan applicants.

Required Configuration:
    - CREDIT_BUREAU_API_KEY: API key for the credit bureau service
    - CREDIT_BUREAU_API_URL: Base URL for the credit bureau API
    - CREDIT_BUREAU_PROVIDER: One of 'equifax', 'experian', 'transunion'

API Contract:
    POST /v1/credit-reports
    Request:
        {
            "ssn": "XXX-XX-XXXX",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }
    Response:
        {
            "report_id": "rpt_abc123",
            "credit_score": 740,
            "score_model": "FICO8",
            "total_accounts": 12,
            "open_accounts": 8,
            "delinquent_accounts": 0,
            "total_balance": 45000.00,
            "monthly_payments": 1200.00,
            "bankruptcies": 0,
            "collections": 0,
            "hard_inquiries_last_12m": 2,
            "report_date": "2024-01-15T10:30:00Z",
            "tradelines": [...],
            "public_records": [...]
        }
"""

import random
from dataclasses import dataclass


@dataclass
class CreditBureauResponse:
    bureau: str
    credit_score: int
    total_accounts: int
    open_accounts: int
    delinquent_accounts: int
    total_balance: float
    monthly_payments: float
    bankruptcies: int
    collections: int
    hard_inquiries_last_12m: int
    report_data: str


class CreditBureauClient:
    """
    Client for interacting with Credit Bureau APIs.

    In production, replace the simulate_* methods with actual API calls
    to credit bureau endpoints.
    """

    def __init__(self, api_key: str | None = None, api_url: str | None = None, provider: str = "equifax"):
        self.api_key = api_key
        self.api_url = api_url or "https://api.creditbureau.example.com/v1"
        self.provider = provider

    def pull_credit_report(
        self,
        ssn_last_four: str,
        first_name: str,
        last_name: str,
        date_of_birth: str,
    ) -> CreditBureauResponse:
        """
        Pull a credit report for the given borrower.

        In production, this would make an HTTP request to the credit bureau API.
        Currently returns simulated data for development/testing.
        """
        return self._simulate_credit_pull(ssn_last_four)

    def _simulate_credit_pull(self, ssn_last_four: str) -> CreditBureauResponse:
        """Generate simulated credit data for development."""
        seed = int(ssn_last_four) if ssn_last_four.isdigit() else 5000
        rng = random.Random(seed)

        credit_score = rng.randint(580, 850)
        total_accounts = rng.randint(3, 25)
        open_accounts = rng.randint(2, min(total_accounts, 15))

        delinquent = 0
        if credit_score < 650:
            delinquent = rng.randint(1, 3)
        elif credit_score < 700:
            delinquent = rng.randint(0, 1)

        return CreditBureauResponse(
            bureau=self.provider,
            credit_score=credit_score,
            total_accounts=total_accounts,
            open_accounts=open_accounts,
            delinquent_accounts=delinquent,
            total_balance=round(rng.uniform(5000, 200000), 2),
            monthly_payments=round(rng.uniform(200, 5000), 2),
            bankruptcies=1 if credit_score < 600 and rng.random() < 0.3 else 0,
            collections=rng.randint(0, 2) if credit_score < 650 else 0,
            hard_inquiries_last_12m=rng.randint(0, 6),
            report_data='{"simulated": true}',
        )


credit_bureau_client = CreditBureauClient()
