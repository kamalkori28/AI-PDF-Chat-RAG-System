import logging

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings

logger = logging.getLogger(__name__)


class ChunkingService:
    """Split PDF pages into retrieval-friendly chunks."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def split(self, documents: list[Document]) -> list[Document]:
        """Split documents with semantic chunking when configured and available."""
        if self.settings.chunk_strategy == "semantic":
            semantic_chunks = self._try_semantic_split(documents)
            if semantic_chunks:
                return semantic_chunks

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_documents(documents)

    def _try_semantic_split(self, documents: list[Document]) -> list[Document]:
        try:
            from langchain_experimental.text_splitter import SemanticChunker

            embeddings = OllamaEmbeddings(
                model=self.settings.ollama_embedding_model,
                base_url=self.settings.ollama_base_url,
                client_kwargs={"timeout": self.settings.ollama_request_timeout_seconds},
            )
            splitter = SemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold_type="percentile",
                min_chunk_size=max(200, self.settings.chunk_size // 3),
            )
            return splitter.split_documents(documents)
        except Exception:
            logger.exception("Semantic chunking failed; falling back to recursive splitting")
            return []
