# API

Base URL: `http://localhost:8000/api/v1`

## Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/login/json`
- `GET /auth/me`

## Documents

- `POST /upload`
- `GET /documents`
- `DELETE /documents?document_id=<uuid>`

## Chat

- `POST /chat`
- `POST /chat/stream`
- `GET /history`
- `GET /history/{session_id}`
- `WS /ws/chat?token=<jwt>`

`POST /chat/stream` emits `metadata`, `token`, `done`, and `error` server-sent events.

## Health

- `GET /health`
- `GET /health/ready`

`GET /health` returns degraded status when Ollama is offline. `GET /health/ready` returns `503` until the database is reachable and Ollama has both `llama3` and `nomic-embed-text` available.

All document and chat endpoints require `Authorization: Bearer <token>`.
