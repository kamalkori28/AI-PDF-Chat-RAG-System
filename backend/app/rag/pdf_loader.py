import asyncio
from pathlib import Path
from uuid import UUID

from langchain_core.documents import Document
from pypdf import PdfReader


class PDFLoader:
    """Load PDF text while preserving page-level metadata."""

    async def load(
        self,
        path: Path,
        *,
        document_id: UUID,
        user_id: UUID,
        filename: str,
    ) -> list[Document]:
        return await asyncio.to_thread(
            self._load_sync,
            path,
            document_id,
            user_id,
            filename,
        )

    def _load_sync(
        self,
        path: Path,
        document_id: UUID,
        user_id: UUID,
        filename: str,
    ) -> list[Document]:
        reader = PdfReader(str(path))
        documents: list[Document] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text(extraction_mode="layout") or ""
            text = " ".join(text.split())
            if not text:
                continue
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "document_id": str(document_id),
                        "user_id": str(user_id),
                        "filename": filename,
                        "page": index,
                        "source": str(path),
                    },
                )
            )
        return documents

