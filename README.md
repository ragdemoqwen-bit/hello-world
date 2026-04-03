# LoanOS - Loan Origination System

A comprehensive loan origination platform for banks, built with FastAPI (Python) and React (TypeScript).

## Architecture

```
loan-origination-backend/     # FastAPI backend
  app/
    main.py                   # Application entry point
    database.py               # SQLite database setup
    models/                   # SQLAlchemy models
    schemas/                  # Pydantic request/response schemas
    routers/                  # API route handlers
    services/                 # Business logic (underwriting engine)
    external/                 # External system integration interfaces
loan-origination-frontend/    # React + TypeScript frontend
  src/
    pages/                    # Page components
    services/                 # API client
```

## Features

### Loan Origination Workflow
1. **Application Intake** - Multi-step form for borrower and loan details
2. **Document Management** - Upload and track required documents by loan type
3. **Credit Check** - Pull credit reports and scores
4. **KYC/Identity Verification** - Verify borrower identity, AML, sanctions
5. **Employment & Income Verification** - Confirm employment status and income
6. **Property Appraisal** - Order and retrieve property valuations (mortgage)
7. **Automated Underwriting** - Risk scoring, DTI/LTV calculations, decisioning
8. **Loan Offer Generation** - Calculate terms, rates, monthly payments
9. **Offer Acceptance & E-Signature** - Digital signing of loan documents
10. **Funding** - Final disbursement

### Underwriting Engine
- Credit score evaluation (FICO-based thresholds)
- Debt-to-Income (DTI) ratio calculation
- Loan-to-Value (LTV) ratio for secured loans
- Composite risk scoring (0-100 scale)
- Automated decisioning: Approved / Conditionally Approved / Denied / Manual Review

### External System Integrations (API Interfaces)
All external integrations include documented API contracts and simulated responses for development:

| Integration | Provider Examples | Module |
|---|---|---|
| Credit Bureau | Equifax, Experian, TransUnion | `external/credit_bureau.py` |
| KYC/Identity | Jumio, Onfido, Persona | `external/kyc_verification.py` |
| Employment Verification | Plaid, The Work Number | `external/employment_verification.py` |
| Property Appraisal | CoreLogic, Clear Capital | `external/property_appraisal.py` |
| E-Signature | DocuSign, HelloSign | `external/esignature.py` |

Each module documents the required configuration (API keys, URLs) and the full API contract (request/response format) needed for production integration.

## Running Locally

### Backend
```bash
cd loan-origination-backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd loan-origination-frontend
npm install
npm run dev
```

The frontend runs at http://localhost:5173 and connects to the backend at http://localhost:8000.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/applications` | Submit new loan application |
| GET | `/api/applications` | List applications (filterable) |
| GET | `/api/applications/{id}` | Get application details |
| GET | `/api/applications/{id}/full-details` | Get complete application with all related data |
| PUT | `/api/applications/{id}/status` | Update application status |
| GET | `/api/applications/{id}/status-history` | Get status audit trail |
| POST | `/api/applications/{id}/credit-check` | Run credit check |
| POST | `/api/applications/{id}/kyc-verification` | Run KYC verification |
| POST | `/api/applications/{id}/employment-verification` | Run employment verification |
| POST | `/api/applications/{id}/property-appraisal` | Order property appraisal |
| POST | `/api/applications/{id}/underwrite` | Run automated underwriting |
| POST | `/api/applications/{id}/generate-offer` | Generate loan offer |
| POST | `/api/applications/{id}/accept-offer` | Accept or decline offer |
| POST | `/api/applications/{id}/fund` | Fund the loan |
| POST | `/api/documents/{id}/upload` | Upload document |
| GET | `/api/documents/{id}` | List documents |
| GET | `/api/documents/{id}/required` | Get required documents checklist |
| GET | `/api/dashboard/stats` | Dashboard statistics |
