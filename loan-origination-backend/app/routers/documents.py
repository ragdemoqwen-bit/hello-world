import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication, ApplicationStatus
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.status_history import StatusHistory
from app.schemas.document import DocumentResponse, DocumentVerification

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/{application_id}/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a document for a loan application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Validate document type
    try:
        DocumentType(document_type)
    except ValueError:
        valid_types = [dt.value for dt in DocumentType]
        raise HTTPException(status_code=400, detail=f"Invalid document type. Valid types: {valid_types}")

    # Save file
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "document")[1]
    file_name = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    document = Document(
        application_id=application_id,
        document_type=document_type,
        file_name=file.filename or "document",
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/{application_id}", response_model=list[DocumentResponse])
def list_documents(application_id: str, db: Session = Depends(get_db)):
    """List all documents for an application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    documents = (
        db.query(Document)
        .filter(Document.application_id == application_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return documents


@router.put("/{document_id}/verify", response_model=DocumentResponse)
def verify_document(
    document_id: str,
    payload: DocumentVerification,
    db: Session = Depends(get_db),
):
    """Verify or reject a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        DocumentStatus(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'verified' or 'rejected'")

    document.status = payload.status
    if payload.status == DocumentStatus.VERIFIED:
        document.verified_at = datetime.utcnow()
    elif payload.status == DocumentStatus.REJECTED:
        document.rejection_reason = payload.rejection_reason

    db.commit()
    db.refresh(document)
    return document


@router.get("/{application_id}/required")
def get_required_documents(application_id: str, db: Session = Depends(get_db)):
    """Get the list of required documents based on loan type."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Base documents required for all loan types
    required = [
        {"type": DocumentType.ID_DOCUMENT.value, "label": "Government-issued ID"},
        {"type": DocumentType.PROOF_OF_ADDRESS.value, "label": "Proof of Address"},
        {"type": DocumentType.PAY_STUB.value, "label": "Recent Pay Stubs (last 2 months)"},
        {"type": DocumentType.W2.value, "label": "W-2 Forms (last 2 years)"},
        {"type": DocumentType.BANK_STATEMENT.value, "label": "Bank Statements (last 3 months)"},
    ]

    if application.loan_type == "mortgage":
        required.extend([
            {"type": DocumentType.TAX_RETURN.value, "label": "Tax Returns (last 2 years)"},
            {"type": DocumentType.PROPERTY_APPRAISAL.value, "label": "Property Appraisal Report"},
            {"type": DocumentType.TITLE_REPORT.value, "label": "Title Report"},
            {"type": DocumentType.INSURANCE_PROOF.value, "label": "Homeowner's Insurance"},
        ])
    elif application.loan_type == "auto":
        required.append({"type": DocumentType.INSURANCE_PROOF.value, "label": "Auto Insurance Proof"})
    elif application.loan_type == "business":
        required.extend([
            {"type": DocumentType.TAX_RETURN.value, "label": "Business Tax Returns (last 2 years)"},
        ])

    # Check which are already uploaded
    uploaded = (
        db.query(Document)
        .filter(Document.application_id == application_id)
        .all()
    )
    uploaded_types = {doc.document_type for doc in uploaded}

    for doc in required:
        doc["uploaded"] = doc["type"] in uploaded_types
        matching = [d for d in uploaded if d.document_type == doc["type"]]
        doc["status"] = matching[0].status if matching else "not_uploaded"

    return required
