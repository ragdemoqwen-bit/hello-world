from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    application_id: str
    document_type: str
    file_name: str
    file_path: str
    file_size: int | None = None
    mime_type: str | None = None
    status: str
    rejection_reason: str | None = None
    uploaded_at: datetime
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentVerification(BaseModel):
    status: str
    rejection_reason: str | None = None
