import hashlib
import logging
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.db.session import async_engine
from app.models.document import UploadedDocument
from app.models.user import User
from app.rag.chunking import ChunkingService
from app.rag.pdf_loader import PDFLoader
from app.rag.vector_store import VectorStoreService
from app.utils.sanitization import sanitize_filename

logger = logging.getLogger(__name__)


class DocumentService:
    """Handle PDF upload, persistence, ingestion, and deletion."""

    def __init__(self, db: AsyncSession | None = None, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    async def save_uploads(self, *, user: User, files: list[UploadFile]) -> list[UploadedDocument]:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded.",
            )

        documents: list[UploadedDocument] = []
        for file in files:
            documents.append(await self._save_one(user=user, file=file))

        await self.db.commit()
        return documents

    async def list_user_documents(self, user: User) -> list[UploadedDocument]:
        result = await self.db.execute(
            select(UploadedDocument)
            .where(UploadedDocument.user_id == user.id)
            .order_by(UploadedDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_documents(self, *, user: User, document_id: UUID | None = None) -> int:
        vector_store = VectorStoreService(self.settings)
        if document_id:
            result = await self.db.execute(
                select(UploadedDocument).where(
                    UploadedDocument.id == document_id,
                    UploadedDocument.user_id == user.id,
                )
            )
            document = result.scalar_one_or_none()
            if document is None:
                return 0
            await vector_store.delete_by_document(user_id=user.id, document_id=document.id)
            self._delete_file(document.stored_filename)
            await self.db.delete(document)
            await self.db.commit()
            return 1

        documents = await self.list_user_documents(user)
        await vector_store.delete_all_for_user(user_id=user.id)
        for document in documents:
            self._delete_file(document.stored_filename)
        await self.db.execute(delete(UploadedDocument).where(UploadedDocument.user_id == user.id))
        await self.db.commit()
        return len(documents)

    async def _save_one(self, *, user: User, file: UploadFile) -> UploadedDocument:
        original_name = sanitize_filename(file.filename or "document.pdf")
        if not original_name.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"{original_name} is not a PDF file.",
            )

        content_type = file.content_type or "application/pdf"
        if content_type not in {"application/pdf", "application/octet-stream"}:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type: {content_type}.",
            )

        stored_filename = f"{user.id}/{uuid4()}-{original_name}"
        destination = self.settings.upload_dir / stored_filename
        destination.parent.mkdir(parents=True, exist_ok=True)

        sha256 = hashlib.sha256()
        size = 0
        async with aiofiles.open(destination, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > self.settings.max_upload_size_bytes:
                    await out_file.close()
                    destination.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"{original_name} exceeds {self.settings.max_upload_size_mb} MB.",
                    )
                sha256.update(chunk)
                await out_file.write(chunk)

        document = UploadedDocument(
            user_id=user.id,
            filename=original_name,
            stored_filename=stored_filename,
            content_type=content_type,
            file_size=size,
            sha256=sha256.hexdigest(),
            status="queued",
            document_metadata={"original_name": original_name},
        )
        self.db.add(document)
        await self.db.flush()
        return document

    def _delete_file(self, stored_filename: str) -> None:
        path = self.settings.upload_dir / stored_filename
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Failed to delete uploaded file %s", path)

    @staticmethod
    async def process_document_task(document_id: UUID, settings: Settings | None = None) -> None:
        """Background task entry point for PDF ingestion."""
        settings = settings or get_settings()
        session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
        async with session_factory() as db:
            result = await db.execute(
                select(UploadedDocument).where(UploadedDocument.id == document_id)
            )
            document = result.scalar_one_or_none()
            if document is None:
                return

            document.status = "processing"
            await db.commit()

            try:
                path = Path(settings.upload_dir / document.stored_filename)
                pages = await PDFLoader().load(
                    path,
                    document_id=document.id,
                    user_id=document.user_id,
                    filename=document.filename,
                )
                chunks = await ChunkingService(settings).split(pages)
                chunk_count = await VectorStoreService(settings).add_documents(
                    documents=chunks,
                    document_id=document.id,
                )
                document.status = "ready"
                document.chunk_count = chunk_count
                document.error_message = None
                document.document_metadata = {
                    **(document.document_metadata or {}),
                    "pages_extracted": len(pages),
                    "chunk_strategy": settings.chunk_strategy,
                }
            except Exception as exc:
                logger.exception("Document ingestion failed for %s", document_id)
                document.status = "failed"
                document.error_message = str(exc)[:1000]
            finally:
                await db.commit()
