"""
E-Signature / Document Signing Integration

External Dependency: E-Signature Service (e.g., DocuSign, HelloSign, PandaDoc)
-------------------------------------------------------------------------------
In production, this module integrates with e-signature platforms to send
loan documents for digital signing during the closing process.

Required Configuration:
    - ESIGN_API_KEY: API key for the e-signature service
    - ESIGN_ACCOUNT_ID: Account/integration ID
    - ESIGN_WEBHOOK_URL: Webhook URL for status updates
    - ESIGN_TEMPLATE_IDS: Mapping of document types to template IDs

API Contract (DocuSign-style):
    POST /v2.1/accounts/{accountId}/envelopes
    Request:
        {
            "emailSubject": "Loan Documents - Please Sign",
            "documents": [
                {
                    "documentBase64": "...",
                    "name": "Loan Agreement",
                    "fileExtension": "pdf",
                    "documentId": "1"
                }
            ],
            "recipients": {
                "signers": [
                    {
                        "email": "john.doe@email.com",
                        "name": "John Doe",
                        "recipientId": "1",
                        "tabs": {
                            "signHereTabs": [{"documentId": "1", "pageNumber": "5", "xPosition": "100", "yPosition": "500"}]
                        }
                    }
                ]
            },
            "status": "sent"
        }
    Response:
        {
            "envelopeId": "env_abc123",
            "status": "sent",
            "statusDateTime": "2024-01-15T10:30:00Z",
            "uri": "/envelopes/env_abc123"
        }

    GET /v2.1/accounts/{accountId}/envelopes/{envelopeId}
    Response:
        {
            "envelopeId": "env_abc123",
            "status": "completed",
            "completedDateTime": "2024-01-15T15:45:00Z",
            "documents": [...]
        }
"""

import random
from dataclasses import dataclass


@dataclass
class ESignatureResult:
    envelope_id: str
    status: str
    signing_url: str | None = None


class ESignatureClient:
    """
    Client for E-Signature APIs.

    In production, replace simulate methods with actual DocuSign
    or HelloSign API calls.
    """

    def __init__(self, api_key: str | None = None, account_id: str | None = None):
        self.api_key = api_key
        self.account_id = account_id

    def send_for_signature(
        self,
        borrower_email: str,
        borrower_name: str,
        document_name: str,
        application_id: str,
    ) -> ESignatureResult:
        """
        Send loan documents for electronic signature.

        In production, this creates an envelope/signing request
        with the e-signature provider.
        """
        return self._simulate_signing_request(application_id)

    def check_status(self, envelope_id: str) -> ESignatureResult:
        """Check the status of a signing request."""
        return self._simulate_status_check(envelope_id)

    def _simulate_signing_request(self, application_id: str) -> ESignatureResult:
        """Generate simulated e-signature results."""
        rng = random.Random(hash(application_id))
        envelope_id = f"env_{rng.randint(100000, 999999)}"

        return ESignatureResult(
            envelope_id=envelope_id,
            status="sent",
            signing_url=f"https://esign.example.com/sign/{envelope_id}",
        )

    def _simulate_status_check(self, envelope_id: str) -> ESignatureResult:
        """Simulate checking signing status."""
        return ESignatureResult(
            envelope_id=envelope_id,
            status="completed",
            signing_url=None,
        )


esignature_client = ESignatureClient()
