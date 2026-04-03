"""
Property Appraisal Integration

External Dependency: Appraisal Management Service (e.g., CoreLogic, MISMO, Clear Capital)
------------------------------------------------------------------------------------------
In production, this module integrates with appraisal management companies (AMCs)
to order and retrieve property appraisals for mortgage loans.

Required Configuration:
    - APPRAISAL_API_KEY: API key for the appraisal service
    - APPRAISAL_API_URL: Base URL

API Contract:
    POST /v1/appraisals/order
    Request:
        {
            "property_address": {
                "street": "456 Oak Ave",
                "city": "Springfield",
                "state": "IL",
                "zip": "62702"
            },
            "property_type": "single_family",
            "loan_type": "conventional",
            "requested_amount": 280000.00,
            "contact": {
                "name": "John Doe",
                "phone": "555-123-4567"
            }
        }
    Response:
        {
            "appraisal_id": "apr_def456",
            "status": "ordered",
            "estimated_completion": "2024-01-25",
            "appraiser_name": "Jane Smith, MAI",
            "appraiser_license": "IL-12345"
        }

    GET /v1/appraisals/{appraisal_id}
    Response:
        {
            "appraisal_id": "apr_def456",
            "status": "completed",
            "appraised_value": 310000.00,
            "property_condition": "good",
            "property_type": "single_family",
            "year_built": 1995,
            "living_area_sqft": 2100,
            "lot_size_sqft": 8500,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "comparable_sales": [...],
            "report_pdf_url": "https://...",
            "completed_at": "2024-01-23T14:00:00Z"
        }
"""

import random
from dataclasses import dataclass


@dataclass
class AppraisalResult:
    appraisal_id: str
    status: str
    appraised_value: float
    property_condition: str


class PropertyAppraisalClient:
    """
    Client for Property Appraisal APIs.

    In production, replace simulate methods with actual AMC API calls.
    """

    def __init__(self, api_key: str | None = None, api_url: str | None = None):
        self.api_key = api_key
        self.api_url = api_url or "https://api.appraisal-service.example.com/v1"

    def order_appraisal(
        self,
        property_address: str,
        requested_amount: float,
    ) -> AppraisalResult:
        """
        Order a property appraisal.

        In production, this would create an appraisal order through the AMC API.
        """
        return self._simulate_appraisal(requested_amount)

    def _simulate_appraisal(self, requested_amount: float) -> AppraisalResult:
        """Generate simulated appraisal results."""
        rng = random.Random(int(requested_amount))
        variance = rng.uniform(-0.15, 0.2)
        appraised_value = requested_amount * (1 + variance)

        conditions = ["excellent", "good", "fair", "poor"]
        weights = [0.15, 0.55, 0.25, 0.05]
        condition = rng.choices(conditions, weights=weights, k=1)[0]

        return AppraisalResult(
            appraisal_id=f"apr_{rng.randint(100000, 999999)}",
            status="completed",
            appraised_value=round(appraised_value, 2),
            property_condition=condition,
        )


property_appraisal_client = PropertyAppraisalClient()
