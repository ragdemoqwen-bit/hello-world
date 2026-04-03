from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication, ApplicationStatus
from app.models.loan_offer import LoanOffer, OfferStatus

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get summary statistics for the loan origination dashboard."""
    total = db.query(func.count(LoanApplication.id)).scalar() or 0
    by_status = (
        db.query(LoanApplication.status, func.count(LoanApplication.id))
        .group_by(LoanApplication.status)
        .all()
    )
    by_type = (
        db.query(LoanApplication.loan_type, func.count(LoanApplication.id))
        .group_by(LoanApplication.loan_type)
        .all()
    )

    total_requested = db.query(func.sum(LoanApplication.requested_amount)).scalar() or 0
    total_funded = (
        db.query(func.sum(LoanApplication.requested_amount))
        .filter(LoanApplication.status == ApplicationStatus.FUNDED)
        .scalar()
    ) or 0

    approved_count = (
        db.query(func.count(LoanApplication.id))
        .filter(
            LoanApplication.status.in_([
                ApplicationStatus.APPROVED,
                ApplicationStatus.CONDITIONALLY_APPROVED,
                ApplicationStatus.LOAN_OFFERED,
                ApplicationStatus.OFFER_ACCEPTED,
                ApplicationStatus.CLOSING,
                ApplicationStatus.FUNDED,
            ])
        )
        .scalar()
    ) or 0

    denied_count = (
        db.query(func.count(LoanApplication.id))
        .filter(LoanApplication.status == ApplicationStatus.DENIED)
        .scalar()
    ) or 0

    pending_count = (
        db.query(func.count(LoanApplication.id))
        .filter(
            LoanApplication.status.in_([
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.DOCUMENTS_PENDING,
                ApplicationStatus.CREDIT_CHECK,
                ApplicationStatus.KYC_VERIFICATION,
                ApplicationStatus.EMPLOYMENT_VERIFICATION,
                ApplicationStatus.APPRAISAL,
                ApplicationStatus.UNDERWRITING,
            ])
        )
        .scalar()
    ) or 0

    return {
        "total_applications": total,
        "total_requested_amount": total_requested,
        "total_funded_amount": total_funded,
        "approved_count": approved_count,
        "denied_count": denied_count,
        "pending_count": pending_count,
        "approval_rate": round(approved_count / total * 100, 1) if total > 0 else 0,
        "by_status": {status: count for status, count in by_status},
        "by_type": {loan_type: count for loan_type, count in by_type},
    }
