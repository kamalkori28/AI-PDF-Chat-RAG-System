# Deployment

## Local Docker

```bash
ollama pull llama3
ollama pull nomic-embed-text
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker compose up --build
```

Install and start Ollama on the host before running Docker. Keep `OLLAMA_BASE_URL=http://host.docker.internal:11434` for containers. Replace `SECRET_KEY` in the root `.env` file before production use.

Required Ollama setup:

```bash
ollama pull llama3
ollama pull nomic-embed-text
ollama list
```

Frontend: `http://localhost:3000`

Backend docs: `http://localhost:8000/docs`

## Render

Use `render.yaml` as a Blueprint only when you have a network-accessible Ollama server. For fully local/offline use, prefer Docker Compose on the same machine as Ollama.

## Railway

Create separate Railway services for:

- PostgreSQL
- Backend using `backend/Dockerfile`
- Frontend using `frontend/Dockerfile`

Set:

- `DATABASE_URL`
- `SECRET_KEY`
- `OLLAMA_BASE_URL`
- `OLLAMA_CHAT_MODEL`
- `OLLAMA_EMBEDDING_MODEL`
- `NEXT_PUBLIC_API_URL`
- `BACKEND_CORS_ORIGINS`

## Vercel

Deploy the `frontend` folder and set:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.example.com/api/v1
```

Deploy the backend separately on Render, Railway, Fly.io, or EC2.

## AWS EC2

1. Install Docker and Docker Compose.
2. Copy the repo to the instance.
3. Create an `.env` file next to `deploy/aws-ec2/docker-compose.prod.yml`.
4. Run:

```bash
docker compose -f deploy/aws-ec2/docker-compose.prod.yml up -d --build
```

Use a reverse proxy such as Nginx or Caddy for TLS and domain routing.

When Ollama runs on the same EC2 host as Docker, keep:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Docker Build Hygiene

The backend and frontend Docker contexts include `.dockerignore` files. Keep local runtime artifacts such as `.venv`, `node_modules`, `.next`, `storage`, and SQLite databases out of images and source control.
