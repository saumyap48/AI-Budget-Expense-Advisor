# AI Budget & Expense Advisor (Full Stack + Gemini AI + RAG)

A production-grade personal finance web application where users can manage daily expenses, set and track monthly budgets, visualize spending analytics via interactive charts, and consult an AI assistant powered by **Retrieval-Augmented Generation (RAG)** using **Google Gemini 2.5 Flash** (`google.genai` SDK), **PostgreSQL**, and **ChromaDB**.

---

## 🌟 Features

- 💳 **Full Expense Lifecycle (CRUD)**: Record, update, search, filter by category, and delete transactions with instant state synchronization.
- 🎯 **Monthly Budgeting & Alerts**: Dynamic budget utilization tracking with visual warnings when spending exceeds 80% and alerts when over 100%.
- 📊 **Interactive Data Analytics**: Visual dashboards powered by Chart.js featuring daily, weekly, and monthly spending trend lines, category distribution charts, daily average calculations, and top spending categories.
- 🤖 **Gemini AI Financial Assistant**: Grounded AI chatbot answering questions based **strictly on your personal expense data** using ChromaDB vector search and Google Gemini (`gemini-2.5-flash` via `google.genai` SDK).
- 🛡️ **Zero-Hallucination RAG Pipeline**: Strict prompt guardrails and multi-user context isolation prevent unverified financial numbers or cross-user data leaks.
- ☁️ **Production & Cloud Ready**: Fully compatible with PostgreSQL (Render) and local SQLite storage. Configured for Render deployment using dynamic `$PORT` binding.

---

## 🏗️ Architecture Overview

```text
User (Browser) <---> Vanilla JS Frontend (Fetch API + Chart.js)
                             │
                     FastAPI Backend (REST API)
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
  PostgreSQL / SQLite    ChromaDB            Gemini API
(Expenses, Budget, Auth) (Vector DB)   (gemini-2.5-flash via google.genai)
```

### RAG Pipeline Flow

```text
User Question
      ↓
FastAPI /api/v1/chat
      ↓
RAGService
      ↓
ChromaDB semantic retrieval (user_id filtered)
      +
PostgreSQL financial / analytics context
      ↓
Context + Prompt Guardrails
      ↓
Gemini 2.5 Flash (google.genai SDK)
      ↓
AI Response
```

*(Note: Ollama / Llama 3 is not part of this implementation; all AI queries run through Google Gemini 2.5 Flash via `google.genai`.)*

---

## 📁 Folder Structure

```text
AI-Budget-Expense-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                     # App factory & FastAPI startup
│   │   ├── core/                       # Configuration, DB engine, logger & security
│   │   ├── models/                     # SQLAlchemy ORM Models (User, Expense, Budget)
│   │   ├── schemas/                    # Pydantic request/response validation DTOs
│   │   ├── repositories/               # Repository pattern for database abstraction
│   │   ├── services/                   # Business logic, ChromaDB & RAG orchestrator
│   │   │   ├── gemini_service.py       # Google Gemini API integration (google.genai SDK)
│   │   │   ├── rag_service.py          # RAG context retriever & prompt constructor
│   │   │   ├── chroma_service.py       # Vector DB collection & similarity search
│   │   │   ├── analytics_service.py    # Metric & trend computations
│   │   │   └── budget_service.py       # Budget utilization math
│   │   ├── routes/                     # Versioned REST API endpoints (/api/v1)
│   │   ├── middleware/                 # Request logging & error translation
│   │   └── prompts/                    # Financial prompt templates
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                            # ⚠️ Not committed — add GEMINI_API_KEY & DATABASE_URL
│
├── frontend/
│   ├── index.html                      # Single Page Application HTML
│   ├── css/                            # Glassmorphism dark mode design system
│   └── js/                             # ES6 modular components (charts, chat, budget)
│
├── render.yaml                         # Render deployment specification
├── README.md
└── .gitignore
```

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla Glassmorphism), JavaScript (ES6 Modules), Chart.js
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL / SQLite, Pydantic v2, Passlib (Argon2), PyJWT
- **AI & RAG**: Google Gemini API (`gemini-2.5-flash` via `google.genai`), ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Deployment**: Render (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)

---

## 🚀 Setup & Execution Guide

### Prerequisites
1. **Python 3.11+** installed.
2. **PostgreSQL** or local SQLite.
3. A **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey).

### Step 1: Configure Environment
Copy `.env.example` to `.env` inside the `backend/` folder and add your Gemini API key:
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env`:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-2.5-flash"
DATABASE_URL="postgresql+psycopg2://expense_user:password@localhost:5432/expense_tracker"
```

### Step 2: Install Backend Dependencies
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Launch FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Step 4: Render Cloud Deployment
Render deployment automatically binds to `$PORT` and initializes PostgreSQL connection pooling via:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 📄 License

MIT License
