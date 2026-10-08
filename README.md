# KnowledgeOps AI

**Enterprise AI Knowledge Management & RAG Platform**

KnowledgeOps AI is a full-stack AI knowledge assistant that lets users upload organizational documents and ask questions about their content using Retrieval-Augmented Generation (RAG).

It combines **FastAPI, React, PostgreSQL, ChromaDB, LangGraph, Groq, and Ollama** to provide a practical document intelligence and conversational knowledge platform.

## 🚀 Live Demo

**Try the application:**  
https://knowledge-ops-ai-three.vercel.app/

**GitHub Repository:**  
https://github.com/sejaldongre/KnowledgeOps-AI

> The live demo uses Groq for online LLM inference. Local development also supports Ollama for offline inference.

---

### How to Use the Live Demo

The application is publicly deployed and does not require shared demo credentials.

**Demo flow:**

1. Open the live application.
2. Click **Create an account** and register with your email and password.
3. Sign in to access your KnowledgeOps AI workspace.
4. Go to **Documents** and upload a PDF, DOCX, or TXT document.
5. Open **Chat** and ask questions about the uploaded document.
6. Select the preferred LLM mode:
   - **Online** — Groq-powered responses for faster production inference.
   - **Offline** — Ollama-powered local inference for development/testing.
7. Review the retrieved document sources supporting the generated answer.

The platform uses retrieval-augmented generation (RAG) to retrieve relevant document context before generating responses.

## 📌 What It Does

KnowledgeOps AI turns company documents into a searchable knowledge base.

Users can:

- Create and manage documents
- Upload PDF, DOCX, and TXT files
- Create new document versions
- Search documents semantically
- Ask natural-language questions
- Get answers grounded in retrieved document content
- View the sources used for an answer
- Use online Groq inference or local Ollama inference
- Access documents through authentication and permissions

### Example

**Question**

> How many paid annual leave days does a full-time employee receive per year?

**Answer**

> Full-time employees receive 20 days of paid annual leave per calendar year.

---

## 🧠 How RAG Works

```text
DOCUMENT INGESTION

PDF / DOCX / TXT
       │
       ▼
Text Extraction
       │
       ▼
Text Cleaning
       │
       ▼
Document Chunking
       │
       ├──────────────► PostgreSQL
       │                 (persistent source of truth)
       │
       ▼
Embedding Generation
       │
       ▼
ChromaDB
(Vector Search Index)


QUESTION ANSWERING

User Question
       │
       ▼
FastAPI
       │
       ▼
LangGraph RAG Workflow
       │
       ▼
Semantic Retrieval
       │
       ▼
Relevant Document Chunks
       │
       ▼
Prompt Construction
       │
       ├──────────────► Groq
       │                 (Online)
       │
       └──────────────► Ollama
                         (Offline)
       │
       ▼
Grounded Answer
       │
       ▼
Sources + Response
```

---

## ✨ Key Features

### 📄 Document Management

- PDF, DOCX, and TXT document support
- Document metadata management
- Document versioning
- Processing status tracking
- Persistent document chunks in PostgreSQL

### 🔍 Semantic Search

- Embedding-based document retrieval
- ChromaDB vector search
- Configurable retrieval limit
- Relevant source chunks returned with responses

### 🤖 RAG Assistant

- Retrieval-Augmented Generation
- LangGraph workflow
- Query refinement
- Context-aware prompt construction
- Grounded responses
- No-context handling for unsupported questions

### 🔐 Authentication & Permissions

- JWT authentication
- Password hashing
- Protected API routes
- Document-level permissions
- Owner-based access control
- VIEW / EDIT / DELETE permissions

### ⚡ Online & Offline LLM Modes

**Online:** Uses Groq for fast cloud-based LLM inference.

**Offline:** Uses Ollama and a locally installed model, allowing the RAG workflow to run locally without depending on a cloud LLM.

### 📚 Source-Aware Answers

The chat interface displays retrieved sources so users can inspect the document context used to generate an answer.

---

## 🏗️ System Architecture

```text
┌───────────────────────────────┐
│        React + Vite           │
│          Frontend             │
└───────────────┬───────────────┘
                │ REST API
                ▼
┌───────────────────────────────┐
│           FastAPI             │
│           Backend             │
├───────────────────────────────┤
│ Authentication                │
│ Permissions / RBAC             │
│ Document Management           │
│ Document Processing            │
│ RAG / LangGraph               │
└───────┬───────────┬───────────┘
        │           │
        ▼           ▼
┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │  ChromaDB   │
│ Users       │  │ Embeddings  │
│ Documents   │  │ Retrieval   │
│ Versions    │  │ Vector Index│
│ Chunks      │  └──────┬──────┘
└─────────────┘         │
                        ▼
                ┌───────────────┐
                │   LangGraph   │
                │   RAG Flow    │
                └───────┬───────┘
                        │
                 ┌──────┴──────┐
                 ▼             ▼
            ┌─────────┐   ┌─────────┐
            │  Groq   │   │ Ollama  │
            │ Online  │   │ Offline │
            └─────────┘   └─────────┘
```

---

## 🔄 RAG Workflow

KnowledgeOps AI uses a multi-stage workflow built with LangGraph.

```text
START
  │
  ▼
Retrieve
  │
  ▼
Refine Query
  │
  ▼
Build Prompt
  │
  ▼
Generate
  │
  ▼
END
```

If the initial retrieval is insufficient, the workflow can refine the query before generating the final response.

If relevant knowledge cannot be found, the system can return a no-context response rather than relying on unsupported information.

---

## ♻️ Vector Index Persistence

A key deployment challenge was the persistence of ChromaDB on the free Render environment.

The application therefore treats:

- **PostgreSQL as the persistent source of truth**
- **ChromaDB as a rebuildable vector search index**

Document chunks are stored in PostgreSQL. When the backend starts, the application rebuilds the ChromaDB index from the current document chunks.

```text
Backend Startup
      │
      ▼
Read Current Document Chunks
from PostgreSQL
      │
      ▼
Clear Chroma Collection
      │
      ▼
Recreate Vector Index
      │
      ▼
FastAPI Ready
```

This allows the RAG system to recover its vector search index after a backend restart or redeployment without requiring users to upload their documents again.

---

## 🛠️ Tech Stack

| Layer               | Technologies             |
| ------------------- | ------------------------ |
| Frontend            | React, TypeScript, Vite  |
| Backend             | Python, FastAPI, Uvicorn |
| Database            | PostgreSQL               |
| ORM / Migrations    | SQLAlchemy, Alembic      |
| RAG Orchestration   | LangGraph                |
| Vector Database     | ChromaDB                 |
| Online LLM          | Groq                     |
| Offline LLM         | Ollama                   |
| Authentication      | JWT, Argon2              |
| Document Processing | PyPDF, python-docx       |
| HTTP Client         | Axios, HTTPX             |
| Containerization    | Docker                   |
| Frontend Deployment | Vercel                   |
| Backend Deployment  | Render                   |
| Source Control      | Git, GitHub              |

---

## 📁 Project Structure

```text
KnowledgeOps-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── infrastructure/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   │       ├── graph/
│   │       ├── llm/
│   │       ├── document_processing.py
│   │       ├── document_chunking.py
│   │       ├── document_extraction.py
│   │       ├── document_text_cleaning.py
│   │       ├── vector_store.py
│   │       └── vector_index_rebuild.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── data/
├── docker/
├── docs/
├── scripts/
├── tests/
├── .gitignore
└── README.md
```

---

## 💻 Local Development

### Prerequisites

- Python 3.11+
- Node.js
- Docker Desktop
- Ollama
- Git

### 1. Clone

```bash
git clone https://github.com/sejaldongre/KnowledgeOps-AI.git
cd KnowledgeOps-AI
```

### 2. Backend

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Environment variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/knowledgeops

JWT_SECRET_KEY=your-secret-key

LLM_DEFAULT_MODE=offline

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

OLLAMA_BASE_URL=http://localhost:11434
OFFLINE_LLM_MODEL=llama3.2:3b
```

**Never commit real API keys or secrets to GitHub.**

### 5. Database migrations

From `backend/`:

```bash
alembic upgrade head
```

### 6. Ollama

```bash
ollama pull llama3.2:3b
ollama serve
```

### 7. Start backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 8. Start frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

For local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 🌐 Deployment

### Frontend

The React frontend is deployed on **Vercel**.

```text
GitHub → Vercel → React + Vite
```

### Backend

The FastAPI backend is containerized with Docker and deployed on **Render**.

```text
GitHub → Docker Build → Render → FastAPI
```

### Database

PostgreSQL is hosted using Render PostgreSQL.

---

## 🧪 Testing

The application was tested across the main RAG workflows.

### Supported question

```text
How many paid annual leave days does a full-time employee receive per year?
```

Expected result:

```text
20 days of paid annual leave per calendar year.
```

### Unsupported questions

Questions for information not present in the knowledge base were tested to ensure the system indicates that the information is unavailable instead of fabricating a policy.

### Persistence test

The vector persistence behavior was tested by:

1. Indexing a document.
2. Restarting the backend.
3. Rebuilding Chroma automatically from PostgreSQL.
4. Asking a question without uploading the document again.
5. Successfully retrieving the correct answer.

### Production verification

The deployed application was also tested after deployment without manually uploading a new document version.

---

## 📡 API Overview

### Authentication

```text
POST /auth/login
GET  /auth/me
```

### Documents

```text
GET  /documents
POST /documents
POST /documents/{document_id}/upload
```

### Chat

```text
POST /chat
```

### Search

```text
POST /search
```

### Health

```text
GET /health
GET /health/database
```

Interactive API documentation is available through FastAPI at `/docs`.

---

## 🔐 Security

The project includes:

- JWT authentication
- Argon2 password hashing
- Protected API endpoints
- Document-level authorization
- Owner-based access control
- Environment-based secret configuration

API keys and credentials should always be stored in environment variables and never committed to the repository.

---

## ⚠️ Current Limitations

KnowledgeOps AI is a **portfolio-grade working RAG platform**, rather than a large-scale enterprise production system.

Current limitations include:

- ChromaDB is filesystem-based and rebuilt from PostgreSQL when required.
- The current deployment uses free-tier infrastructure.
- Local Ollama inference is slower than cloud LLM inference.
- Large-scale workloads would require a managed vector database and additional infrastructure.
- Document processing is currently handled by the application rather than a dedicated background job system.

---

## 🚀 Future Improvements

- Managed vector database
- Redis caching
- Background document processing
- OCR for scanned documents
- Hybrid keyword + semantic search
- Retrieval reranking
- Streaming LLM responses
- More advanced conversation memory
- Object storage for uploaded documents
- Production monitoring and observability
- Automated CI/CD testing
- Advanced analytics dashboard

---

## 🎯 What This Project Demonstrates

- Retrieval-Augmented Generation (RAG)
- Generative AI and LLM integration
- Semantic search and vector databases
- LangGraph workflows
- Document processing
- FastAPI backend development
- React frontend development
- PostgreSQL
- Authentication and authorization
- Docker
- Cloud deployment
- Production debugging
- Data persistence and recovery strategies

---

## 👩‍💻 Author

**Sejal Dongre**

AI Engineer | Machine Learning | Generative AI | RAG

**GitHub:**  
https://github.com/sejaldongre

**Project Repository:**  
https://github.com/sejaldongre/KnowledgeOps-AI

**Live Demo:**  
https://knowledge-ops-ai-three.vercel.app/

---

## ⭐ Project Summary

**KnowledgeOps AI is a full-stack AI knowledge management and RAG platform that enables users to upload organizational documents and interact with them through a permission-aware AI assistant. It combines FastAPI, React, PostgreSQL, ChromaDB, LangGraph, Groq, and Ollama to provide grounded document question answering with online and offline LLM support.**
