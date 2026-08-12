# 💰 AI Budget & Expense Advisor

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

# 🏗️ Architecture

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

# 🔄 RAG Pipeline

```text
AI-Budget-Expense-Advisor/
│
├── backend/
│   │
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
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── app.js
│       ├── api.js
│       ├── authManager.js
│       ├── expenseManager.js
│       ├── budgetTracker.js
│       ├── analyticsView.js
│       ├── chartManager.js
│       ├── chatWidget.js
│       └── store.js
│
├── render.yaml                         # Render deployment specification
├── README.md
└── .gitignore
```

---

# 🔑 Authentication Flow

- **Frontend**: HTML5, CSS3 (Vanilla Glassmorphism), JavaScript (ES6 Modules), Chart.js
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL / SQLite, Pydantic v2, Passlib (Argon2), PyJWT
- **AI & RAG**: Google Gemini API (`gemini-2.5-flash` via `google.genai`), ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Deployment**: Render (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)

---

# 💸 Expense Flow

### Prerequisites
1. **Python 3.11+** installed.
2. **PostgreSQL** or local SQLite.
3. A **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey).

```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env`:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-2.5-flash"
DATABASE_URL="postgresql+psycopg2://expense_user:password@localhost:5432/expense_tracker"
```

---

# 🗃️ Database Schema

## Users

```text
users
├── id
├── full_name
├── email
├── password_hash
├── created_at
└── updated_at
```

## Expenses

```text
expenses
├── id
├── user_id
├── amount
├── category
├── description
├── date
├── payment_method
├── notes
├── created_at
└── updated_at
```

## Budgets

```text
budgets
├── id
├── user_id
├── monthly_budget
├── month
├── year
├── created_at
└── updated_at
```

---

# 🗂️ PostgreSQL vs ChromaDB

| PostgreSQL           | ChromaDB                 |
| -------------------- | ------------------------ |
| Users                | Expense document vectors |
| Exact expenses       | Semantic representations |
| Budgets              | Expense metadata         |
| Transactions         | Similarity search        |
| SQL aggregation      | Vector retrieval         |
| Relational integrity | RAG context              |

Both databases have different responsibilities.

**PostgreSQL handles structured source-of-truth financial data, while ChromaDB supports semantic retrieval for the RAG pipeline.**

---

# ⚙️ Environment Variables

Create a `.env` file inside `backend/`.

Example:

```env
APP_NAME=AI Budget & Expense Advisor
APP_ENV=development
DEBUG=true

HOST=127.0.0.1
PORT=8000

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker_test

CHROMA_DB_DIR=./vector_store/chroma_db
CHROMA_COLLECTION_NAME=expense_vectors

GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

LLM_PROVIDER=gemini

ALLOWED_ORIGINS=http://127.0.0.1:8080
```

**Never commit the real `.env` file or API keys.**

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/saumyap48/AI-Budget-Expense-Advisor.git

cd AI-Budget-Expense-Advisor
```

## 2. Create Virtual Environment

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment

Create:

```text
backend/.env
```

Configure your PostgreSQL database and Gemini API credentials.

## 5. Run Database Migrations

```bash
python -m alembic upgrade head
```

## 6. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 4: Render Cloud Deployment
Render deployment automatically binds to `$PORT` and initializes PostgreSQL connection pooling via:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

# 📈 Performance & Reliability

The application uses:

* PostgreSQL indexes
* SQL aggregation
* Pagination
* Vector similarity search
* Modular service architecture
* Automated testing
* Database migration management with Alembic
* Expense/vector synchronization on create, update, and delete operations

---

# 📸 Screenshots

Add screenshots of:

* Dashboard
* Expense Management
* Budget Tracker
* Analytics
* AI Financial Advisor

Example:

```markdown
![Dashboard](screenshots/dashboard.png)
![Expenses](screenshots/expenses.png)
![Analytics](screenshots/analytics.png)
![AI Advisor](screenshots/ai-advisor.png)
```

---

# 📄 Resume Description

### Short Version

> Built an AI-powered Personal Finance & Expense Advisor using FastAPI, PostgreSQL, SQLAlchemy, ChromaDB, and Google Gemini. Implemented a Retrieval-Augmented Generation (RAG) pipeline that retrieves user-specific expense context and financial metrics to generate personalized AI-powered financial insights.

### Technical Version

> Developed a full-stack personal finance platform using Vanilla JavaScript and FastAPI, implementing JWT authentication, PostgreSQL-based expense and budget management, ChromaDB vector retrieval, and a custom RAG pipeline. Integrated Google Gemini 2.5 Flash to generate context-aware financial responses while enforcing user-level vector isolation and automatic expense-vector synchronization.

---

# 🎤 Interview Explanation

### "Does your project use RAG?"

> **Yes. My project uses a custom Retrieval-Augmented Generation pipeline. When a user asks a financial question, the system retrieves relevant expense documents from ChromaDB using semantic similarity and also retrieves structured financial metrics such as spending totals and budget information from PostgreSQL. RAGService combines this context into a prompt and sends it to Gemini 2.5 Flash, which generates the final personalized response.**

### "Why did you use RAG?"

> **The LLM does not inherently know the user's private expense history. RAG allows the application to retrieve relevant user-specific information first and provide that context to the LLM, allowing the response to be grounded in the application's actual financial data.**

### "Why PostgreSQL and ChromaDB?"

> **PostgreSQL is used for structured and transactional financial data, while ChromaDB is used for semantic vector retrieval. PostgreSQL provides exact calculations and relational integrity, while ChromaDB helps retrieve relevant expense context for the RAG pipeline.**

### "Which LLM are you using?"

> **The active LLM in my project is Google Gemini 2.5 Flash. It receives the context retrieved by my RAG pipeline and generates the final financial response.**

---

# 🌐 Repository

GitHub repository:

https://github.com/saumyap48/AI-Budget-Expense-Advisor

---

# 📜 License

MIT License
