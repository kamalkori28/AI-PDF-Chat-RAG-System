import asyncio
import re
from functools import cached_property
from uuid import UUID

from fastapi import HTTPException, status
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from app.core.config import Settings
from app.utils.cache import TTLCache

_SEARCH_CACHE = TTLCache(ttl_seconds=300)


class VectorStoreService:
    """ChromaDB backed vector-store access layer."""

    def __init__(self, settings: Settings) -> None:
        global _SEARCH_CACHE

        self.settings = settings
        if _SEARCH_CACHE.ttl_seconds != settings.cache_ttl_seconds:
            _SEARCH_CACHE = TTLCache(ttl_seconds=settings.cache_ttl_seconds)

    @cached_property
    def embeddings(self) -> OllamaEmbeddings:
        return OllamaEmbeddings(
            model=self.settings.ollama_embedding_model,
            base_url=self.settings.ollama_base_url,
            client_kwargs={"timeout": self.settings.ollama_request_timeout_seconds},
        )

    @cached_property
    def store(self) -> Chroma:
        self.settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        return Chroma(
            collection_name=self.settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.settings.chroma_persist_dir),
        )

    async def add_documents(self, documents: list[Document], document_id: UUID) -> int:
        if not documents:
            return 0

        ids: list[str] = []
        for index, document in enumerate(documents):
            chunk_id = f"{document_id}:{index}"
            document.metadata["chunk_id"] = chunk_id
            ids.append(chunk_id)

        try:
            await asyncio.to_thread(self.store.add_documents, documents=documents, ids=ids)
        except Exception as exc:
            raise self._ollama_unavailable_error("embedding documents") from exc
        _SEARCH_CACHE.clear()
        return len(documents)

    async def search(
        self,
        *,
        query: str,
        user_id: UUID,
        top_k: int,
        document_ids: list[UUID] | None = None,
        hybrid: bool = True,
    ) -> list[tuple[Document, float]]:
        cache_key = (
            query,
            str(user_id),
            top_k,
            tuple(str(document_id) for document_id in document_ids or []),
            hybrid,
        )
        cached = _SEARCH_CACHE.get(cache_key)
        if cached is not None:
            return cached

        metadata_filter = self._metadata_filter(user_id=user_id, document_ids=document_ids)
        try:
            raw_results = await asyncio.to_thread(
                self.store.similarity_search_with_score,
                query,
                max(top_k * 3, top_k),
                filter=metadata_filter,
            )
        except Exception as exc:
            raise self._ollama_unavailable_error("retrieving documents") from exc
        scored = [(doc, self._distance_to_similarity(score)) for doc, score in raw_results]
        if hybrid:
            scored = self._keyword_rerank(query, scored)
        results = scored[:top_k]
        _SEARCH_CACHE.set(cache_key, results)
        return results

    async def delete_by_document(self, *, user_id: UUID, document_id: UUID) -> None:
        metadata_filter = {
            "$and": [
                {"user_id": str(user_id)},
                {"document_id": str(document_id)},
            ]
        }
        await asyncio.to_thread(self.store.delete, where=metadata_filter)
        _SEARCH_CACHE.clear()

    async def delete_all_for_user(self, *, user_id: UUID) -> None:
        await asyncio.to_thread(
            self.store.delete,
            where={"user_id": str(user_id)},
        )
        _SEARCH_CACHE.clear()

    def _metadata_filter(
        self,
        *,
        user_id: UUID,
        document_ids: list[UUID] | None,
    ) -> dict:
        if not document_ids:
            return {"user_id": str(user_id)}
        return {
            "$and": [
                {"user_id": str(user_id)},
                {"document_id": {"$in": [str(document_id) for document_id in document_ids]}},
            ]
        }

    def _keyword_rerank(
        self,
        query: str,
        docs: list[tuple[Document, float]],
    ) -> list[tuple[Document, float]]:
        query_terms = set(re.findall(r"[a-zA-Z0-9]{3,}", query.lower()))
        if not query_terms:
            return docs

        reranked: list[tuple[Document, float]] = []
        for document, semantic_score in docs:
            content_terms = set(re.findall(r"[a-zA-Z0-9]{3,}", document.page_content.lower()))
            lexical_overlap = len(query_terms & content_terms) / max(len(query_terms), 1)
            reranked.append((document, semantic_score + (0.12 * lexical_overlap)))
        return sorted(reranked, key=lambda item: item[1], reverse=True)

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        return 1.0 / (1.0 + max(distance, 0.0))

    def _ollama_unavailable_error(self, action: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Unable to reach Ollama while {action}. Start Ollama and run "
                f"`ollama pull {self.settings.ollama_embedding_model}`. "
                f"Configured OLLAMA_BASE_URL={self.settings.ollama_base_url}."
            ),
        )
