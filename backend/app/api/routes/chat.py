import json
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.deps import CurrentUserDep, DbSessionDep, SettingsDep
from app.core.security import decode_access_token
from app.db.session import async_engine
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionRead, HistoryResponse
from app.services.chat_service import ChatService
from app.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    settings: SettingsDep,
) -> ChatResponse:
    """Generate a grounded RAG answer for the authenticated user."""
    return await ChatService(db=db, settings=settings).answer(
        user=current_user,
        payload=payload,
    )


@router.post("/chat/stream")
async def stream_chat(
    payload: ChatRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    settings: SettingsDep,
) -> StreamingResponse:
    """Stream a RAG answer as server-sent events."""
    service = ChatService(db=db, settings=settings)

    async def event_stream():
        try:
            async for event in service.stream_answer(user=current_user, payload=payload):
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
        except HTTPException as exc:
            data = {"detail": exc.detail, "status_code": exc.status_code}
            yield f"event: error\ndata: {json.dumps(data)}\n\n"
        except Exception:
            logger.exception("Streaming chat failed")
            data = {"detail": "Unable to generate a response.", "status_code": 500}
            yield f"event: error\ndata: {json.dumps(data)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, settings: SettingsDep) -> None:
    """WebSocket streaming chat endpoint.

    Clients pass `?token=<jwt>` and then send ChatRequest-shaped JSON messages.
    """
    await websocket.accept()
    token = websocket.query_params.get("token")
    token_data = decode_access_token(token=token or "", settings=settings)
    if token_data is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with session_factory() as db:
        user = await UserService(db).get_by_id(UUID(token_data.sub))
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            while True:
                raw_payload = await websocket.receive_json()
                payload = ChatRequest.model_validate(raw_payload)
                service = ChatService(db=db, settings=settings)
                try:
                    async for event in service.stream_answer(user=user, payload=payload):
                        await websocket.send_json(event)
                except HTTPException as exc:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": {"detail": exc.detail, "status_code": exc.status_code},
                        }
                    )
                except Exception:
                    logger.exception("WebSocket chat failed")
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": {
                                "detail": "Unable to generate a response.",
                                "status_code": 500,
                            },
                        }
                    )
        except WebSocketDisconnect:
            return


@router.get("/history", response_model=HistoryResponse)
async def history(
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> HistoryResponse:
    """List chat sessions for the current user."""
    sessions = await ChatService(db=db).list_sessions(current_user)
    return HistoryResponse(sessions=sessions)


@router.get("/history/{session_id}", response_model=ChatSessionRead)
async def session_history(
    session_id: UUID,
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> ChatSessionRead:
    """Return one chat session and its messages."""
    return await ChatService(db=db).get_session(current_user, session_id)
