from types import SimpleNamespace

import pytest

from app.schemas.chat import Citation


class FakeRAGPipeline:
    def __init__(self, settings) -> None:
        self.settings = settings

    async def retrieve(self, **kwargs):
        return SimpleNamespace(
            context_text="[Source 1]\ncontent: Enterprise RAG context",
            citations=[
                Citation(
                    label="Source 1",
                    document_id="doc-1",
                    filename="enterprise.pdf",
                    page=1,
                    chunk_id="doc-1:0",
                    score=0.99,
                    preview="Enterprise RAG context",
                )
            ],
            documents=[],
        )

    async def generate(self, **kwargs) -> str:
        return "The answer is grounded in the uploaded PDF. [Source 1]"


async def auth_headers(client) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "chat@example.com",
            "full_name": "Chat User",
            "password": "secure-password",
        },
    )
    response = await client.post(
        "/api/v1/auth/login/json",
        json={"email": "chat@example.com", "password": "secure-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_chat_persists_session_and_citations(client, monkeypatch):
    from app.services import chat_service

    monkeypatch.setattr(chat_service, "RAGPipeline", FakeRAGPipeline)
    headers = await auth_headers(client)

    response = await client.post(
        "/api/v1/chat",
        headers=headers,
        json={"message": "What is this document about?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("The answer is grounded")
    assert payload["citations"][0]["filename"] == "enterprise.pdf"

    history = await client.get("/api/v1/history", headers=headers)
    assert history.status_code == 200
    sessions = history.json()["sessions"]
    assert len(sessions) == 1
    assert len(sessions[0]["messages"]) == 2

