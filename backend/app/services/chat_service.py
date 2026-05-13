from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings, get_settings
from app.models.chat import ChatSession, Message
from app.models.user import User
from app.rag.pipeline import RAGPipeline
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionRead, Citation


class ChatService:
    """Service layer for conversation persistence and RAG orchestration."""

    def __init__(self, db: AsyncSession, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.rag = RAGPipeline(self.settings)

    async def answer(self, *, user: User, payload: ChatRequest) -> ChatResponse:
        try:
            session = await self._get_or_create_session(user=user, payload=payload)
            await self._create_message(
                session=session,
                user=user,
                role="user",
                content=payload.message,
            )
            history = await self._format_history(session.id)
            context = await self.rag.retrieve(
                query=payload.message,
                user_id=user.id,
                top_k=payload.top_k,
                document_ids=payload.document_ids,
                hybrid=payload.hybrid,
            )
            answer = await self.rag.generate(
                question=payload.message,
                history=history,
                context=context,
            )
            await self._create_message(
                session=session,
                user=user,
                role="assistant",
                content=answer,
                citations=context.citations,
            )
            await self.db.commit()
            return ChatResponse(
                session_id=session.id,
                answer=answer,
                citations=context.citations,
            )
        except Exception:
            await self.db.rollback()
            raise

    async def stream_answer(self, *, user: User, payload: ChatRequest):
        try:
            session = await self._get_or_create_session(user=user, payload=payload)
            await self._create_message(
                session=session,
                user=user,
                role="user",
                content=payload.message,
            )
            await self.db.flush()

            history = await self._format_history(session.id)
            context = await self.rag.retrieve(
                query=payload.message,
                user_id=user.id,
                top_k=payload.top_k,
                document_ids=payload.document_ids,
                hybrid=payload.hybrid,
            )

            yield {
                "type": "metadata",
                "data": {
                    "session_id": str(session.id),
                    "citations": [citation.model_dump() for citation in context.citations],
                },
            }

            answer_parts: list[str] = []
            async for token in self.rag.stream(
                question=payload.message,
                history=history,
                context=context,
            ):
                answer_parts.append(token)
                yield {"type": "token", "data": {"token": token}}

            answer = "".join(answer_parts)
            await self._create_message(
                session=session,
                user=user,
                role="assistant",
                content=answer,
                citations=context.citations,
            )
            await self.db.commit()
            yield {"type": "done", "data": {"answer": answer, "session_id": str(session.id)}}
        except Exception:
            await self.db.rollback()
            raise

    async def list_sessions(self, user: User) -> list[ChatSessionRead]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user.id)
            .options(selectinload(ChatSession.messages))
            .order_by(ChatSession.updated_at.desc())
        )
        return [ChatSessionRead.model_validate(session) for session in result.scalars()]

    async def get_session(self, user: User, session_id: UUID) -> ChatSessionRead:
        session = await self._load_session(user=user, session_id=session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
        return ChatSessionRead.model_validate(session)

    async def _get_or_create_session(
        self,
        *,
        user: User,
        payload: ChatRequest,
    ) -> ChatSession:
        if payload.session_id:
            session = await self._load_session(user=user, session_id=payload.session_id)
            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found.",
                )
            return session

        title = payload.message.strip().replace("\n", " ")[:80] or "New chat"
        session = ChatSession(user_id=user.id, title=title)
        self.db.add(session)
        await self.db.flush()
        return session

    async def _load_session(self, *, user: User, session_id: UUID) -> ChatSession | None:
        statement: Select[tuple[ChatSession]] = (
            select(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.user_id == user.id)
            .options(selectinload(ChatSession.messages))
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def _format_history(self, session_id: UUID) -> str:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(self.settings.conversation_window_messages)
        )
        messages = list(reversed(result.scalars().all()))
        return "\n".join(f"{message.role}: {message.content}" for message in messages)

    async def _create_message(
        self,
        *,
        session: ChatSession,
        user: User,
        role: str,
        content: str,
        citations: list[Citation] | None = None,
    ) -> Message:
        message = Message(
            session_id=session.id,
            user_id=user.id,
            role=role,
            content=content,
            citations=[citation.model_dump() for citation in citations] if citations else None,
        )
        self.db.add(message)
        await self.db.flush()
        return message
