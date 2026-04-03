"""
KYC (Know Your Customer) / Identity Verification Integration

External Dependency: KYC/Identity Verification Provider (e.g., Jumio, Onfido, Persona)
---------------------------------------------------------------------------------------
In production, this module integrates with identity verification services
to verify borrower identity, check sanctions lists, and perform AML checks.

Required Configuration:
    - KYC_API_KEY: API key for the KYC provider
    - KYC_API_URL: Base URL for the KYC API
    - KYC_WEBHOOK_SECRET: Secret for verifying webhook callbacks

API Contract:
    POST /v1/verifications
    Request:
        {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "ssn_last_four": "1234",
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            },
            "document_front_url": "https://...",
            "document_back_url": "https://...",
            "selfie_url": "https://..."
        }
    Response:
        {
            "verification_id": "ver_xyz789",
            "status": "verified",  // verified, failed, pending_review
            "identity_match": true,
            "address_match": true,
            "sanctions_clear": true,
            "pep_check": false,
            "aml_check": "clear",
            "risk_score": 15,
            "document_authenticity": "genuine",
            "checks": {
                "identity": "passed",
                "address": "passed",
                "sanctions": "clear",
                "pep": "clear",
                "aml": "clear"
            }
        }
"""

import random
from dataclasses import dataclass


@dataclass
class KYCResult:
    verification_id: str
    status: str
    identity_match: bool
    address_match: bool
    sanctions_clear: bool
    pep_check: bool
    aml_check: str
    risk_score: int


class KYCVerificationClient:
    """
    Client for KYC/Identity Verification APIs.

    In production, replace simulate methods with actual API calls.
    """

    def __init__(self, api_key: str | None = None, api_url: str | None = None):
        self.api_key = api_key
        self.api_url = api_url or "https://api.kyc-provider.example.com/v1"

    def verify_identity(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        ssn_last_four: str,
        address_street: str,
        address_city: str,
        address_state: str,
        address_zip: str,
    ) -> KYCResult:
        """
        Verify borrower identity.

        In production, this would call the KYC provider API with
        borrower details and uploaded identity documents.
        """
        return self._simulate_kyc_check(ssn_last_four)

    def _simulate_kyc_check(self, ssn_last_four: str) -> KYCResult:
        """Generate simulated KYC results."""
        seed = int(ssn_last_four) if ssn_last_four.isdigit() else 5000
        rng = random.Random(seed + 100)

        passed = rng.random() > 0.05  # 95% pass rate

        return KYCResult(
            verification_id=f"ver_{rng.randint(100000, 999999)}",
            status="verified" if passed else "failed",
            identity_match=passed,
            address_match=passed or rng.random() > 0.1,
            sanctions_clear=True,
            pep_check=False,
            aml_check="clear",
            risk_score=rng.randint(5, 25) if passed else rng.randint(60, 90),
        )


kyc_client = KYCVerificationClient()
