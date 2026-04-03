import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication, ApplicationStatus
from app.models.borrower import Borrower
from app.models.credit_report import CreditReport
from app.models.underwriting import UnderwritingResult
from app.models.loan_offer import LoanOffer, OfferStatus
from app.models.status_history import StatusHistory
from app.schemas.application import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanApplicationSummary,
    ApplicationStatusUpdate,
)
from app.schemas.credit import CreditReportResponse
from app.schemas.underwriting import UnderwritingResultResponse
from app.schemas.loan_offer import LoanOfferResponse, LoanOfferAccept
from app.external.credit_bureau import credit_bureau_client
from app.external.kyc_verification import kyc_client
from app.external.employment_verification import employment_verification_client
from app.external.property_appraisal import property_appraisal_client
from app.external.esignature import esignature_client
from app.services.underwriting_engine import (
    UnderwritingInput,
    run_underwriting,
    calculate_interest_rate,
    calculate_monthly_payment,
)

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _add_status_history(
    db: Session,
    application_id: str,
    previous_status: str | None,
    new_status: str,
    changed_by: str = "system",
    notes: str | None = None,
):
    history = StatusHistory(
        application_id=application_id,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
        notes=notes,
    )
    db.add(history)


@router.post("", response_model=LoanApplicationResponse, status_code=201)
def create_application(
    payload: LoanApplicationCreate,
    db: Session = Depends(get_db),
):
    """Submit a new loan application with borrower information."""
    borrower = Borrower(**payload.borrower.model_dump())
    db.add(borrower)
    db.flush()

    application = LoanApplication(
        borrower_id=borrower.id,
        loan_type=payload.loan_type,
        requested_amount=payload.requested_amount,
        loan_purpose=payload.loan_purpose,
        loan_term_months=payload.loan_term_months,
        property_address=payload.property_address,
        property_value=payload.property_value,
        vehicle_info=payload.vehicle_info,
        status=ApplicationStatus.SUBMITTED,
    )
    db.add(application)
    db.flush()

    _add_status_history(db, application.id, None, ApplicationStatus.SUBMITTED, notes="Application submitted")
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[LoanApplicationSummary])
def list_applications(
    status: str | None = Query(None),
    loan_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all loan applications with optional filtering."""
    query = db.query(LoanApplication).join(Borrower)
    if status:
        query = query.filter(LoanApplication.status == status)
    if loan_type:
        query = query.filter(LoanApplication.loan_type == loan_type)
    query = query.order_by(LoanApplication.created_at.desc())
    applications = query.offset(skip).limit(limit).all()

    return [
        LoanApplicationSummary(
            id=app.id,
            borrower_name=f"{app.borrower.first_name} {app.borrower.last_name}",
            loan_type=app.loan_type,
            requested_amount=app.requested_amount,
            status=app.status,
            created_at=app.created_at,
        )
        for app in applications
    ]


@router.get("/{application_id}", response_model=LoanApplicationResponse)
def get_application(application_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/{application_id}/status")
def update_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    """Manually update the status of an application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    previous = application.status
    application.status = payload.status
    _add_status_history(db, application_id, previous, payload.status, payload.changed_by, payload.notes)
    db.commit()
    return {"message": "Status updated", "previous_status": previous, "new_status": payload.status}


@router.get("/{application_id}/status-history")
def get_status_history(application_id: str, db: Session = Depends(get_db)):
    """Get the full status history for an application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    history = (
        db.query(StatusHistory)
        .filter(StatusHistory.application_id == application_id)
        .order_by(StatusHistory.created_at.asc())
        .all()
    )
    return [
        {
            "id": h.id,
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "changed_by": h.changed_by,
            "notes": h.notes,
            "created_at": h.created_at.isoformat(),
        }
        for h in history
    ]


# --- Workflow Endpoints ---

@router.post("/{application_id}/credit-check", response_model=CreditReportResponse)
def run_credit_check(application_id: str, db: Session = Depends(get_db)):
    """
    Trigger a credit check for the application.

    External Dependency: Credit Bureau API (Equifax/Experian/TransUnion)
    In production, calls the credit bureau API to pull the borrower's credit report.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if already pulled
    existing = db.query(CreditReport).filter(CreditReport.application_id == application_id).first()
    if existing:
        return existing

    borrower = application.borrower
    result = credit_bureau_client.pull_credit_report(
        ssn_last_four=borrower.ssn_last_four,
        first_name=borrower.first_name,
        last_name=borrower.last_name,
        date_of_birth=borrower.date_of_birth,
    )

    credit_report = CreditReport(
        application_id=application_id,
        bureau=result.bureau,
        credit_score=result.credit_score,
        total_accounts=result.total_accounts,
        open_accounts=result.open_accounts,
        delinquent_accounts=result.delinquent_accounts,
        total_balance=result.total_balance,
        monthly_payments=result.monthly_payments,
        bankruptcies=result.bankruptcies,
        collections=result.collections,
        hard_inquiries_last_12m=result.hard_inquiries_last_12m,
        report_data=result.report_data,
    )
    db.add(credit_report)

    previous = application.status
    application.status = ApplicationStatus.CREDIT_CHECK
    _add_status_history(db, application_id, previous, ApplicationStatus.CREDIT_CHECK, notes=f"Credit score: {result.credit_score}")
    db.commit()
    db.refresh(credit_report)
    return credit_report


@router.post("/{application_id}/kyc-verification")
def run_kyc_verification(application_id: str, db: Session = Depends(get_db)):
    """
    Trigger KYC/identity verification.

    External Dependency: KYC Provider API (Jumio, Onfido, Persona)
    In production, calls the KYC provider to verify borrower identity.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    borrower = application.borrower
    result = kyc_client.verify_identity(
        first_name=borrower.first_name,
        last_name=borrower.last_name,
        date_of_birth=borrower.date_of_birth,
        ssn_last_four=borrower.ssn_last_four,
        address_street=borrower.address_street,
        address_city=borrower.address_city,
        address_state=borrower.address_state,
        address_zip=borrower.address_zip,
    )

    previous = application.status
    application.status = ApplicationStatus.KYC_VERIFICATION
    _add_status_history(
        db, application_id, previous, ApplicationStatus.KYC_VERIFICATION,
        notes=f"KYC {result.status}: identity_match={result.identity_match}",
    )
    db.commit()

    return {
        "verification_id": result.verification_id,
        "status": result.status,
        "identity_match": result.identity_match,
        "address_match": result.address_match,
        "sanctions_clear": result.sanctions_clear,
        "pep_check": result.pep_check,
        "aml_check": result.aml_check,
        "risk_score": result.risk_score,
    }


@router.post("/{application_id}/employment-verification")
def run_employment_verification(application_id: str, db: Session = Depends(get_db)):
    """
    Trigger employment and income verification.

    External Dependency: Employment Verification API (Plaid, The Work Number)
    In production, calls the verification service to confirm employment/income.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    borrower = application.borrower
    result = employment_verification_client.verify_employment(
        employer_name=borrower.employer_name,
        first_name=borrower.first_name,
        last_name=borrower.last_name,
        ssn_last_four=borrower.ssn_last_four,
        stated_income=borrower.annual_income,
    )

    previous = application.status
    application.status = ApplicationStatus.EMPLOYMENT_VERIFICATION
    _add_status_history(
        db, application_id, previous, ApplicationStatus.EMPLOYMENT_VERIFICATION,
        notes=f"Employment {result.status}: verified_income=${result.verified_annual_income:,.2f}",
    )
    db.commit()

    return {
        "verification_id": result.verification_id,
        "status": result.status,
        "employer_verified": result.employer_verified,
        "employment_status": result.employment_status,
        "verified_annual_income": result.verified_annual_income,
        "income_verified": result.income_verified,
        "confidence_score": result.confidence_score,
    }


@router.post("/{application_id}/property-appraisal")
def run_property_appraisal(application_id: str, db: Session = Depends(get_db)):
    """
    Order a property appraisal (for mortgage loans).

    External Dependency: Appraisal Management API (CoreLogic, Clear Capital)
    In production, orders appraisal through AMC and retrieves valuation.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.loan_type != "mortgage":
        raise HTTPException(status_code=400, detail="Property appraisal only applicable for mortgage loans")

    if not application.property_address:
        raise HTTPException(status_code=400, detail="Property address required for appraisal")

    result = property_appraisal_client.order_appraisal(
        property_address=application.property_address,
        requested_amount=application.requested_amount,
    )

    # Update property value with appraisal
    application.property_value = result.appraised_value

    previous = application.status
    application.status = ApplicationStatus.APPRAISAL
    _add_status_history(
        db, application_id, previous, ApplicationStatus.APPRAISAL,
        notes=f"Appraised value: ${result.appraised_value:,.2f}, condition: {result.property_condition}",
    )
    db.commit()

    return {
        "appraisal_id": result.appraisal_id,
        "status": result.status,
        "appraised_value": result.appraised_value,
        "property_condition": result.property_condition,
    }


@router.post("/{application_id}/underwrite", response_model=UnderwritingResultResponse)
def run_underwriting_evaluation(application_id: str, db: Session = Depends(get_db)):
    """
    Run automated underwriting evaluation.

    Requires credit check to be completed first.
    Evaluates credit score, DTI ratio, LTV ratio, and other risk factors.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    credit_report = db.query(CreditReport).filter(CreditReport.application_id == application_id).first()
    if not credit_report:
        raise HTTPException(status_code=400, detail="Credit check must be completed before underwriting")

    # Check if already underwritten
    existing = db.query(UnderwritingResult).filter(UnderwritingResult.application_id == application_id).first()
    if existing:
        return existing

    borrower = application.borrower
    inputs = UnderwritingInput(
        credit_score=credit_report.credit_score,
        annual_income=borrower.annual_income,
        monthly_debt_payments=borrower.monthly_debt_payments,
        requested_amount=application.requested_amount,
        loan_term_months=application.loan_term_months,
        loan_type=application.loan_type,
        property_value=application.property_value,
        bankruptcies=credit_report.bankruptcies,
        collections=credit_report.collections,
        delinquent_accounts=credit_report.delinquent_accounts,
    )

    output = run_underwriting(inputs)

    result = UnderwritingResult(
        application_id=application_id,
        credit_score=output.credit_score,
        dti_ratio=output.dti_ratio,
        ltv_ratio=output.ltv_ratio,
        risk_score=output.risk_score,
        risk_level=output.risk_level.value,
        decision=output.decision.value,
        conditions=json.dumps(output.conditions) if output.conditions else None,
        denial_reasons=json.dumps(output.denial_reasons) if output.denial_reasons else None,
        notes=output.notes,
    )
    db.add(result)

    # Update application status based on decision
    previous = application.status
    status_map = {
        "approved": ApplicationStatus.APPROVED,
        "conditionally_approved": ApplicationStatus.CONDITIONALLY_APPROVED,
        "denied": ApplicationStatus.DENIED,
        "manual_review": ApplicationStatus.UNDERWRITING,
    }
    new_status = status_map.get(output.decision.value, ApplicationStatus.UNDERWRITING)
    application.status = new_status
    _add_status_history(
        db, application_id, previous, new_status,
        notes=f"Underwriting decision: {output.decision.value}, risk: {output.risk_level.value}",
    )
    db.commit()
    db.refresh(result)
    return result


@router.post("/{application_id}/generate-offer", response_model=LoanOfferResponse)
def generate_loan_offer(application_id: str, db: Session = Depends(get_db)):
    """
    Generate a loan offer based on underwriting results.

    Only available for approved or conditionally approved applications.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status not in [ApplicationStatus.APPROVED, ApplicationStatus.CONDITIONALLY_APPROVED]:
        raise HTTPException(status_code=400, detail="Application must be approved before generating offer")

    # Check if offer already exists
    existing = db.query(LoanOffer).filter(LoanOffer.application_id == application_id).first()
    if existing:
        return existing

    underwriting = db.query(UnderwritingResult).filter(UnderwritingResult.application_id == application_id).first()
    if not underwriting:
        raise HTTPException(status_code=400, detail="Underwriting must be completed first")

    # Calculate offer terms
    interest_rate = calculate_interest_rate(
        underwriting.credit_score,
        application.loan_type,
        underwriting.ltv_ratio,
    )
    monthly_payment = calculate_monthly_payment(
        application.requested_amount,
        interest_rate,
        application.loan_term_months,
    )
    total_cost = monthly_payment * application.loan_term_months
    total_interest = total_cost - application.requested_amount
    origination_fee = round(application.requested_amount * 0.01, 2)  # 1% origination fee
    apr = round(interest_rate + 0.002, 4)  # Simplified APR (rate + fee impact)

    offer = LoanOffer(
        application_id=application_id,
        approved_amount=application.requested_amount,
        interest_rate=interest_rate,
        loan_term_months=application.loan_term_months,
        monthly_payment=monthly_payment,
        apr=apr,
        origination_fee=origination_fee,
        total_interest=round(total_interest, 2),
        total_cost=round(total_cost, 2),
        requires_collateral=application.loan_type in ["mortgage", "auto"],
        status=OfferStatus.SENT,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(offer)

    previous = application.status
    application.status = ApplicationStatus.LOAN_OFFERED
    _add_status_history(
        db, application_id, previous, ApplicationStatus.LOAN_OFFERED,
        notes=f"Offer: ${application.requested_amount:,.2f} at {interest_rate:.2%} for {application.loan_term_months} months",
    )
    db.commit()
    db.refresh(offer)
    return offer


@router.post("/{application_id}/accept-offer")
def accept_or_decline_offer(
    application_id: str,
    payload: LoanOfferAccept,
    db: Session = Depends(get_db),
):
    """
    Accept or decline a loan offer.

    If accepted, triggers the closing process including e-signature.
    External Dependency: E-Signature API (DocuSign, HelloSign)
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    offer = db.query(LoanOffer).filter(LoanOffer.application_id == application_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="No offer found for this application")

    if offer.status != OfferStatus.SENT:
        raise HTTPException(status_code=400, detail=f"Offer cannot be acted on in current status: {offer.status}")

    previous = application.status

    if payload.accepted:
        offer.status = OfferStatus.ACCEPTED
        offer.accepted_at = datetime.utcnow()
        application.status = ApplicationStatus.CLOSING

        # Trigger e-signature process
        borrower = application.borrower
        esign_result = esignature_client.send_for_signature(
            borrower_email=borrower.email,
            borrower_name=f"{borrower.first_name} {borrower.last_name}",
            document_name="Loan Agreement",
            application_id=application_id,
        )

        _add_status_history(
            db, application_id, previous, ApplicationStatus.CLOSING,
            notes=f"Offer accepted. E-signature envelope: {esign_result.envelope_id}",
        )
        db.commit()

        return {
            "message": "Offer accepted. Loan documents sent for signing.",
            "signing_url": esign_result.signing_url,
            "envelope_id": esign_result.envelope_id,
        }
    else:
        offer.status = OfferStatus.DECLINED
        application.status = ApplicationStatus.WITHDRAWN
        _add_status_history(
            db, application_id, previous, ApplicationStatus.WITHDRAWN,
            notes="Offer declined by borrower",
        )
        db.commit()
        return {"message": "Offer declined. Application withdrawn."}


@router.post("/{application_id}/fund")
def fund_loan(application_id: str, db: Session = Depends(get_db)):
    """
    Mark loan as funded (final step in origination).

    In production, this would trigger fund disbursement through
    the bank's core banking system.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != ApplicationStatus.CLOSING:
        raise HTTPException(status_code=400, detail="Application must be in closing status to fund")

    previous = application.status
    application.status = ApplicationStatus.FUNDED
    _add_status_history(
        db, application_id, previous, ApplicationStatus.FUNDED,
        notes="Loan funded and disbursed",
    )
    db.commit()
    return {"message": "Loan funded successfully", "application_id": application_id}


@router.get("/{application_id}/full-details")
def get_full_application_details(application_id: str, db: Session = Depends(get_db)):
    """Get complete application details including all related records."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    credit_report = db.query(CreditReport).filter(CreditReport.application_id == application_id).first()
    underwriting = db.query(UnderwritingResult).filter(UnderwritingResult.application_id == application_id).first()
    offer = db.query(LoanOffer).filter(LoanOffer.application_id == application_id).first()
    history = (
        db.query(StatusHistory)
        .filter(StatusHistory.application_id == application_id)
        .order_by(StatusHistory.created_at.asc())
        .all()
    )

    borrower = application.borrower

    result: dict = {
        "application": {
            "id": application.id,
            "loan_type": application.loan_type,
            "requested_amount": application.requested_amount,
            "loan_purpose": application.loan_purpose,
            "loan_term_months": application.loan_term_months,
            "property_address": application.property_address,
            "property_value": application.property_value,
            "vehicle_info": application.vehicle_info,
            "status": application.status,
            "created_at": application.created_at.isoformat(),
            "updated_at": application.updated_at.isoformat(),
        },
        "borrower": {
            "id": borrower.id,
            "name": f"{borrower.first_name} {borrower.last_name}",
            "email": borrower.email,
            "phone": borrower.phone,
            "annual_income": borrower.annual_income,
            "monthly_debt_payments": borrower.monthly_debt_payments,
            "employer_name": borrower.employer_name,
            "job_title": borrower.job_title,
        },
        "credit_report": None,
        "underwriting": None,
        "loan_offer": None,
        "status_history": [
            {
                "previous_status": h.previous_status,
                "new_status": h.new_status,
                "changed_by": h.changed_by,
                "notes": h.notes,
                "created_at": h.created_at.isoformat(),
            }
            for h in history
        ],
    }

    if credit_report:
        result["credit_report"] = {
            "bureau": credit_report.bureau,
            "credit_score": credit_report.credit_score,
            "total_accounts": credit_report.total_accounts,
            "open_accounts": credit_report.open_accounts,
            "delinquent_accounts": credit_report.delinquent_accounts,
            "total_balance": credit_report.total_balance,
            "monthly_payments": credit_report.monthly_payments,
            "bankruptcies": credit_report.bankruptcies,
            "collections": credit_report.collections,
            "pulled_at": credit_report.pulled_at.isoformat(),
        }

    if underwriting:
        result["underwriting"] = {
            "credit_score": underwriting.credit_score,
            "dti_ratio": underwriting.dti_ratio,
            "ltv_ratio": underwriting.ltv_ratio,
            "risk_score": underwriting.risk_score,
            "risk_level": underwriting.risk_level,
            "decision": underwriting.decision,
            "conditions": json.loads(underwriting.conditions) if underwriting.conditions else [],
            "denial_reasons": json.loads(underwriting.denial_reasons) if underwriting.denial_reasons else [],
            "notes": underwriting.notes,
            "decided_at": underwriting.decided_at.isoformat(),
        }

    if offer:
        result["loan_offer"] = {
            "approved_amount": offer.approved_amount,
            "interest_rate": offer.interest_rate,
            "loan_term_months": offer.loan_term_months,
            "monthly_payment": offer.monthly_payment,
            "apr": offer.apr,
            "origination_fee": offer.origination_fee,
            "total_interest": offer.total_interest,
            "total_cost": offer.total_cost,
            "requires_collateral": offer.requires_collateral,
            "status": offer.status,
            "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
            "created_at": offer.created_at.isoformat(),
        }

    return result
