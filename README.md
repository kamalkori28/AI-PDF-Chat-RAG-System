<h1 align="center">📄 Enterprise AI PDF Chat / RAG Assistant</h1>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&pause=1000&color=00F5D4&center=true&vCenter=true&width=900&lines=Enterprise+AI+PDF+Chat+Assistant;Retrieval-Augmented+Generation+(RAG);FastAPI+%7C+Next.js+%7C+LangChain+%7C+Ollama;Multi-PDF+Semantic+Search+Engine;Streaming+Chat+with+Citations;Production-Ready+Docker+Deployment" alt="Typing SVG" />
</p>

<p align="center">
  💡 A scalable AI-powered PDF chatbot platform that enables intelligent document search, semantic retrieval, contextual conversations, and real-time streaming responses using local LLMs.
</p>

---

# 📌 Project Overview

The Enterprise AI PDF Chat Assistant enables users to upload PDFs and interact with documents using advanced AI-powered Retrieval-Augmented Generation (RAG).

This platform combines:

- Semantic Search
- Vector Databases
- Local LLM Inference
- Multi-turn Conversations
- Real-time Streaming
- Secure Authentication

into one modern production-ready AI application.

---

# 🛠️ Tech Stack

## 🚀 Frontend

![Next.js](https://img.shields.io/badge/Next.js-121212?style=for-the-badge&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)

---

## ⚙️ Backend

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT_Auth-121212?style=for-the-badge)
![WebSocket](https://img.shields.io/badge/WebSockets-FF6600?style=for-the-badge)

---

## 🤖 AI / Machine Learning

![LangChain](https://img.shields.io/badge/LangChain-00A67E?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-121212?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-6E56CF?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG_Pipeline-00C896?style=for-the-badge)
![Embeddings](https://img.shields.io/badge/Embeddings-nomic--embed--text-blue?style=for-the-badge)

---

# ✨ Features

## 📄 Intelligent PDF Processing

✅ Multi-PDF upload support  
✅ PDF parsing with metadata extraction  
✅ Background ingestion pipeline  
✅ Persistent vector storage  
✅ Upload validation and file management  

---

## 🤖 AI-Powered RAG Chat

✅ Retrieval-Augmented Generation (RAG)  
✅ Semantic document search  
✅ Multi-turn contextual conversations  
✅ Streaming AI responses  
✅ Local Ollama LLM integration  
✅ Citation-based answers with source previews  

---

## ⚡ Real-Time APIs & Streaming

✅ REST API support  
✅ Server-Sent Events (SSE)  
✅ WebSocket streaming  
✅ FastAPI async architecture  
✅ Production-ready API routing  

---

## 🔐 Authentication & Security

✅ JWT authentication  
✅ Argon2 password hashing  
✅ Session-based chat history  
✅ Request validation  
✅ Rate limiting support  
✅ Secure backend architecture  

---

## 🧠 Vector Database & Embeddings

✅ ChromaDB persistent storage  
✅ Metadata filtering  
✅ Recursive chunking strategy  
✅ Optional semantic chunking  
✅ Local embedding generation using Ollama  

---

## 🎨 Modern Frontend Experience

✅ Responsive Next.js UI  
✅ Dark mode support  
✅ Markdown rendering  
✅ Toast notifications  
✅ Session restoration  
✅ Real-time streaming chat interface  

---

# 📸 Screenshots

## 🖥️ Main Dashboard

<img src="./docs/screenshots/dashboard.png" width="100%" />

---

## 📤 PDF Upload Workflow

<img src="./docs/screenshots/upload.png" width="100%" />

---

## 💬 Streaming Chat with Citations

<img src="./docs/screenshots/chat.png" width="100%" />

---

## 🌙 Dark Mode Interface

<img src="./docs/screenshots/darkmode.png" width="100%" />

---

# 🏗️ System Architecture

```text
                ┌──────────────────────┐
                │     Next.js Frontend │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     FastAPI Backend  │
                └──────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
 ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
 │ PostgreSQL │   │ Upload Store│   │ JWT Auth    │
 └─────────────┘   └─────────────┘   └─────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ LangChain LCEL RAG   │
                └──────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
 ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
 │ PDF Loader  │   │ Ollama LLM │   │ ChromaDB    │
 └─────────────┘   └─────────────┘   └─────────────┘
```

---

# 📂 Project Structure

```bash
enterprise-ai-pdf-chat/
│
├── backend/
├── frontend/
├── deploy/
├── docs/
├── storage/
├── chroma/
│
├── docker-compose.yml
├── railway.json
├── render.yaml
├── vercel.json
├── README.md
└── .env.example
```

---

# 🚀 Quick Start

## 1️⃣ Clone Repository

```bash
git clone YOUR_GITHUB_REPO_LINK
```

---

## 2️⃣ Navigate to Project Folder

```bash
cd enterprise-ai-pdf-chat
```

---

## 3️⃣ Pull Ollama Models

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

---

## 4️⃣ Setup Environment Variables

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

---

## 5️⃣ Start Application

```bash
docker compose up --build
```

---

# 🌐 Application URLs

| Service | URL |
|---|---|
| Frontend | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| Swagger Docs | `http://localhost:8000/docs` |
| Health Check | `http://localhost:8000/api/v1/health` |

---

# ⚙️ Ollama Configuration

Ollama must be running locally before starting the application.

## Docker Environment

```text
http://host.docker.internal:11434
```

## Local Backend Development

```text
http://localhost:11434
```

---

# 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/register` | POST | Register user |
| `/api/v1/auth/login/json` | POST | User login |
| `/api/v1/upload` | POST | Upload PDFs |
| `/api/v1/chat` | POST | Chat with documents |
| `/api/v1/chat/stream` | POST | Streaming chat |
| `/api/v1/history` | GET | Chat history |
| `/api/v1/documents` | DELETE | Remove uploaded docs |
| `/api/v1/health` | GET | Health check |
| `/api/v1/health/ready` | GET | Readiness check |

---

# 🧠 RAG Pipeline

The platform uses a modern Retrieval-Augmented Generation architecture:

✅ PDF Loading  
✅ Recursive Chunking  
✅ Embedding Generation  
✅ Vector Storage with ChromaDB  
✅ Semantic Retrieval  
✅ Context Injection  
✅ LLM Response Generation  
✅ Citation-Based Answers  

---

# 🔐 Authentication & Database

## Authentication

- JWT Access Tokens
- Secure Password Hashing (Argon2)
- Session Management

---

## Database

- PostgreSQL for persistent storage
- User management
- Chat history
- Document metadata
- Session tracking

---

# 🧪 Testing & Quality

## Backend

```bash
cd backend
pytest
ruff check app tests
```

---

## Frontend

```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

---

# 🐳 Deployment

Deployment configurations included for:

✅ Docker Compose  
✅ Render  
✅ Railway  
✅ Vercel  
✅ AWS EC2  

---

# 📈 Future Improvements

🚀 OCR support for scanned PDFs  
🚀 Redis-backed caching  
🚀 Retrieval reranking models  
🚀 Admin analytics dashboard  
🚀 Multi-user collaboration  
🚀 Retrieval evaluation metrics  
🚀 Cloud object storage integration  
🚀 AI agent workflows  

---

# ⭐ Support

If you like this project:

⭐ Star this repository  
🍴 Fork this project  
📢 Share with others  

---

<h3 align="center">🔥 THANK YOU 🔥</h3>