from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.core.config import Settings
from app.rag.vector_store import VectorStoreService
from app.schemas.chat import Citation

RAG_SYSTEM_PROMPT = """You are an enterprise PDF assistant.
Answer only from the retrieved PDF context and the useful conversation history.
If the context does not contain the answer, say you do not have enough information.
Use concise, professional language.
Include inline citations like [Source 1] whenever you use retrieved context.
Never invent page numbers, filenames, policies, numbers, or quotes.
"""


@dataclass(frozen=True)
class RetrievedContext:
    context_text: str
    citations: list[Citation]
    documents: list[Document]


class RAGPipeline:
    """LangChain LCEL based retrieval and answer generation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.vector_store = VectorStoreService(settings)

    async def retrieve(
        self,
        *,
        query: str,
        user_id: UUID,
        top_k: int | None = None,
        document_ids: list[UUID] | None = None,
        hybrid: bool = True,
    ) -> RetrievedContext:
        top_k = top_k or self.settings.retrieval_top_k
        docs_with_scores = await self.vector_store.search(
            query=query,
            user_id=user_id,
            top_k=top_k,
            document_ids=document_ids,
            hybrid=hybrid,
        )

        context_blocks: list[str] = []
        citations: list[Citation] = []
        documents: list[Document] = []

        for index, (document, score) in enumerate(docs_with_scores, start=1):
            metadata = document.metadata
            source_label = f"Source {index}"
            context_blocks.append(
                "\n".join(
                    [
                        f"[{source_label}]",
                        f"filename: {metadata.get('filename', 'unknown')}",
                        f"page: {metadata.get('page', 'unknown')}",
                        f"chunk_id: {metadata.get('chunk_id', 'unknown')}",
                        "content:",
                        document.page_content,
                    ]
                )
            )
            citations.append(
                Citation(
                    label=source_label,
                    document_id=str(metadata.get("document_id", "")),
                    filename=str(metadata.get("filename", "unknown")),
                    page=int(metadata.get("page", 0) or 0),
                    chunk_id=str(metadata.get("chunk_id", "")),
                    score=round(float(score), 4),
                    preview=document.page_content[:280],
                )
            )
            documents.append(document)

        return RetrievedContext(
            context_text="\n\n".join(context_blocks),
            citations=citations,
            documents=documents,
        )

    async def generate(
        self,
        *,
        question: str,
        history: str,
        context: RetrievedContext,
    ) -> str:
        chain = self._build_chain()
        try:
            return await chain.ainvoke(
                {
                    "question": question,
                    "history": history,
                    "context": context.context_text or "No relevant PDF context found.",
                }
            )
        except Exception as exc:
            raise self._ollama_unavailable_error("generating a response") from exc

    async def stream(
        self,
        *,
        question: str,
        history: str,
        context: RetrievedContext,
    ) -> AsyncIterator[str]:
        chain = self._build_chain()
        try:
            async for chunk in chain.astream(
                {
                    "question": question,
                    "history": history,
                    "context": context.context_text or "No relevant PDF context found.",
                }
            ):
                if chunk:
                    yield chunk
        except Exception as exc:
            raise self._ollama_unavailable_error("streaming a response") from exc

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", RAG_SYSTEM_PROMPT),
                (
                    "human",
                    "Conversation history:\n{history}\n\n"
                    "Retrieved PDF context:\n{context}\n\n"
                    "User question:\n{question}\n\n"
                    "Answer with citations:",
                ),
            ]
        )
        llm = ChatOllama(
            model=self.settings.ollama_chat_model,
            base_url=self.settings.ollama_base_url,
            temperature=0.2,
            num_ctx=self.settings.ollama_num_ctx,
            keep_alive=self.settings.ollama_keep_alive,
            client_kwargs={"timeout": self.settings.ollama_request_timeout_seconds},
        )
        return prompt | llm | StrOutputParser()

    def _ollama_unavailable_error(self, action: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Unable to reach Ollama while {action}. Start Ollama and run "
                f"`ollama pull {self.settings.ollama_chat_model}`. "
                f"Configured OLLAMA_BASE_URL={self.settings.ollama_base_url}."
            ),
        )
