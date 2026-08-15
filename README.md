# 💰 AI Budget & Expense Advisor

A production-grade personal finance web application where users can manage daily expenses, set and track monthly budgets, visualize spending analytics via interactive charts, and consult an AI assistant powered by **Retrieval-Augmented Generation (RAG)** using **Google Gemini 2.5 Flash** (`google.genai` SDK), **PostgreSQL**, and **ChromaDB**.

---

## 🌐 Live Deployments

- **Frontend (Vercel)**: [https://ai-budget-expense-advisor.vercel.app](https://ai-budget-expense-advisor.vercel.app)
- **Backend (Render Web Service)**: [https://ai-budget-expense-advisor-4.onrender.com](https://ai-budget-expense-advisor-4.onrender.com)
- **Database (Render PostgreSQL)**: Production managed PostgreSQL database (`ai-budget-expense-db`)

---

## 🌟 Features

- 💳 **Full Expense Lifecycle (CRUD)**: Record, update, search, filter by category, and delete transactions with instant state synchronization.
- 🎯 **Monthly Budgeting & Alerts**: Dynamic budget utilization tracking with visual warnings when spending exceeds 80% and alerts when over 100%.
- 📊 **Interactive Data Analytics**: Visual dashboards powered by Chart.js featuring daily, weekly, and monthly spending trend lines, category distribution charts, daily average calculations, and top spending categories.
- 🤖 **Gemini AI Financial Assistant**: Grounded AI chatbot answering questions based **strictly on your personal expense data** using ChromaDB vector search and Google Gemini (`gemini-2.5-flash` via `google.genai` SDK).
- 🛡️ **Zero-Hallucination RAG Pipeline**: Strict prompt guardrails and multi-user context isolation prevent unverified financial numbers or cross-user data leaks.
- ☁️ **Production & Cloud Ready**: Fully integrated with Render PostgreSQL and Vercel. Production deployments automatically run database migrations via Alembic.

---

# 🏗️ Architecture

```text
User (Browser) <---> Vanilla JS Frontend (Vercel)
                             │
                     FastAPI Backend (Render)
                             │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
   PostgreSQL             ChromaDB            Gemini API
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
ChromaDB semantic retrieval (user_id metadata filtered)
      +
PostgreSQL financial / analytics context
      ↓
Context + Prompt Guardrails
      ↓
Gemini 2.5 Flash (google.genai SDK)
      ↓
Grounded AI Response
```

---

# 🗂️ Database Schema & Storage

## Relational Database: PostgreSQL

### Users Table
```text
users
├── id (PK)
├── full_name
├── email (UNIQUE)
├── password_hash (Argon2id)
├── created_at
└── updated_at
```

### Expenses Table
```text
expenses
├── id (PK)
├── user_id (FK -> users.id)
├── amount
├── category
├── description
├── date
├── payment_method
├── notes
├── created_at
└── updated_at
```

### Budgets Table
```text
budgets
├── id (PK)
├── user_id (FK -> users.id)
├── monthly_budget
├── month
├── year
├── created_at
└── updated_at
```

## Vector Database: ChromaDB

| PostgreSQL (Relational) | ChromaDB (Vector Search) |
| :--- | :--- |
| Users authentication & profiles | Expense document vectors |
| Structured transaction records | Semantic embedding representations |
| Monthly budgets & categories | User-isolated vector metadata |
| SQL aggregations & metrics | Context retrieval for RAG pipeline |

---

# ⚙️ Required Environment Variables

Environment variables are required for deployment.

### Production Environment Variables (Render Web Service)

Set these in your **Render Dashboard** under **Environment Settings**:

| Variable Name | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Render PostgreSQL Internal Database URL | `postgres://user:pass@dpg-xxx-a.oregon-postgres.render.com/expense_db` |
| `SECRET_KEY` | Secret key for signing JWT tokens | `openssl rand -hex 32` |
| `GEMINI_API_KEY` | Google AI Studio API key | `AIzaSy...` |
| `GEMINI_MODEL` | Google Gemini Model ID | `gemini-2.5-flash` |
| `APP_ENV` | Environment identifier | `production` |
| `DEBUG` | Debug mode toggle | `False` |

---

# 🚀 Local Development Setup

## 1. Clone the Repository

```bash
git clone https://github.com/saumyap48/AI-Budget-Expense-Advisor.git
cd AI-Budget-Expense-Advisor
```

## 2. Create Virtual Environment & Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Configure Environment

Create `backend/.env`:

```env
APP_NAME="AI Budget & Expense Advisor"
APP_ENV="development"
DEBUG=True
PORT=8000
HOST="127.0.0.1"

SECRET_KEY="your_jwt_secret_key_here"
DATABASE_URL="postgresql+psycopg2://expense_user:password@localhost:5432/expense_tracker"

GEMINI_API_KEY="your_google_gemini_api_key"
GEMINI_MODEL="gemini-2.5-flash"

ALLOWED_ORIGINS="http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"
```

## 4. Run Migrations & Start Application

```bash
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

# 🎤 Interview & Architecture QA

### "Does your project use RAG?"
> **Yes. The project implements a Retrieval-Augmented Generation pipeline. When a user asks a financial question, RAGService retrieves semantically relevant transaction embeddings from ChromaDB (filtered strictly by `user_id`) and combines them with structured PostgreSQL financial statistics (totals, average daily spend, budget status). This context is injected into Google Gemini 2.5 Flash (`google.genai` SDK) to generate grounded financial advice.**

### "Why PostgreSQL and ChromaDB?"
> **PostgreSQL serves as the relational source of truth for user authentication, transactional integrity, and exact financial metrics. ChromaDB handles high-dimensional vector embeddings of transaction descriptions to support fast semantic search for AI prompt enrichment.**

### "Which LLM provider do you use?"
> **The application exclusively uses Google Gemini 2.5 Flash via the modern `google.genai` SDK.**

---

# 📜 License

MIT License
