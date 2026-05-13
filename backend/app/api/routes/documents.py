from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, Query, UploadFile, status

from app.api.deps import CurrentUserDep, DbSessionDep, SettingsDep
from app.schemas.document import DocumentDeleteResponse, DocumentRead, UploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_documents(
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    settings: SettingsDep,
    files: Annotated[list[UploadFile], File(description="One or more PDF files.")],
) -> UploadResponse:
    """Upload one or more PDFs and queue ingestion."""
    service = DocumentService(db=db, settings=settings)
    documents = await service.save_uploads(user=current_user, files=files)
    for document in documents:
        background_tasks.add_task(
            DocumentService.process_document_task,
            document_id=document.id,
            settings=settings,
        )
    return UploadResponse(documents=documents)


@router.get("/documents", response_model=list[DocumentRead])
async def list_documents(
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> list[DocumentRead]:
    """List uploaded documents for the current user."""
    return await DocumentService(db=db).list_user_documents(current_user)


@router.delete("/documents", response_model=DocumentDeleteResponse)
async def delete_documents(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    settings: SettingsDep,
    document_id: UUID | None = Query(default=None),
) -> DocumentDeleteResponse:
    """Delete one document or all documents owned by the authenticated user."""
    deleted_count = await DocumentService(db=db, settings=settings).delete_documents(
        user=current_user,
        document_id=document_id,
    )
    return DocumentDeleteResponse(deleted_count=deleted_count)

