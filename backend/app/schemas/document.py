from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    sha256: str
    status: str
    chunk_count: int
    error_message: str | None = None
    document_metadata: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    documents: list[DocumentRead]


class DocumentDeleteResponse(BaseModel):
    deleted_count: int

