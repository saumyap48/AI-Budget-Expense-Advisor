# 💰 AI Budget & Expense Advisor

A production-ready full-stack personal finance web application where users can manage daily expenses, set and track monthly budgets, visualize spending analytics, and consult an AI financial assistant powered by **Retrieval-Augmented Generation (RAG)**.

The application uses **FastAPI, PostgreSQL, ChromaDB, and Google Gemini 2.5 Flash through the modern `google.genai` SDK**.

---

## 🌐 Live Deployment

* **Frontend (Vercel):** [https://ai-budget-expense-advisor.vercel.app/](https://ai-budget-expense-advisor.vercel.app/)
* **Backend API (Render):** [https://ai-budget-expense-advisor-4.onrender.com](https://ai-budget-expense-advisor-4.onrender.com)
* **API Documentation:** [https://ai-budget-expense-advisor-4.onrender.com/docs](https://ai-budget-expense-advisor-4.onrender.com/docs)
* **Database:** Render PostgreSQL (`ai-budget-expense-db`)

---

## 🌟 Features

### 💳 Expense Management

* Create, view, update, and delete expenses
* Search and filter transactions
* Category-based filtering
* Payment method tracking
* Expense descriptions and notes
* User-specific expense isolation

### 🎯 Budget Management

* Create and update monthly budgets
* Track budget utilization
* Calculate remaining budget
* Spending percentage calculation
* Warning when spending reaches 80%
* Alert when spending exceeds 100%

### 📊 Financial Analytics

* Total spending
* Transaction count
* Daily average spending
* Category-wise spending
* Top spending categories
* Daily spending trends
* Weekly spending trends
* Monthly spending trends
* Interactive Chart.js visualizations

### 🤖 AI Financial Assistant

The application provides an AI financial assistant using a **custom RAG pipeline**.

Users can ask questions such as:

* "Where am I spending the most?"
* "How much did I spend on food?"
* "What are my biggest expenses?"
* "How can I reduce my spending?"
* "Am I within my monthly budget?"

The system retrieves relevant user-specific financial context before sending it to Gemini.

### 🔐 Authentication & Security

* User registration and login
* JWT-based authentication
* Argon2id password hashing
* Protected API endpoints
* User ownership validation
* User-level ChromaDB filtering
* CORS configuration
* Centralized error handling
* Request logging

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
              ┌──────────────────────┐
              │ Frontend             │
              │ HTML + CSS + JS      │
              │ Chart.js             │
              │ Vercel               │
              └──────────┬───────────┘
                         │
                      REST API
                         │
                         ▼
              ┌──────────────────────┐
              │ FastAPI Backend      │
              │ Render               │
              └──────────┬───────────┘
                         │
            ┌────────────┼─────────────┐
            │            │             │
            ▼            ▼             ▼
       PostgreSQL     ChromaDB     Gemini API
       Relational     Vector DB    Gemini 2.5 Flash
       Database                    google.genai
```

---

# 🔄 RAG Pipeline

The project implements **Retrieval-Augmented Generation (RAG)**.

```text
User Question
      │
      ▼
POST /api/v1/chat
      │
      ▼
RAGService
      │
      ├───────────────► ChromaDB
      │                  │
      │                  ▼
      │           Semantic Retrieval
      │           User-specific vectors
      │
      ├───────────────► PostgreSQL
      │                  │
      │                  ▼
      │           Structured Financial
      │           Statistics & Budget Data
      │
      ▼
Context Construction
      │
      ▼
Prompt Guardrails
      │
      ▼
Gemini 2.5 Flash
(google.genai SDK)
      │
      ▼
Grounded AI Response
      │
      ▼
Frontend
```

### Two Context Sources

The RAG pipeline combines two types of information:

**1. Semantic context — ChromaDB**

ChromaDB retrieves semantically relevant expense documents using vector similarity search.

**2. Structured context — PostgreSQL**

PostgreSQL provides exact financial information such as:

* Total spending
* Category totals
* Average spending
* Budget status
* Monthly financial statistics

These contexts are combined before being sent to Gemini.

---

# 🔐 Multi-User RAG Security

Each user's expense vectors are associated with their user identity.

During retrieval, the system applies a `user_id` metadata filter:

```text
Current User
     │
     ▼
ChromaDB Retrieval
     │
     └── user_id = current_user.id
                │
                ▼
       Only that user's vectors
```

This prevents one user's financial information from being included in another user's AI context.

The same ownership principle is enforced for PostgreSQL queries.

---

# 🗄️ Database Architecture

The application uses two storage systems with different responsibilities.

## PostgreSQL

PostgreSQL is the **relational source of truth**.

It stores:

* User accounts
* Password hashes
* Expenses
* Budgets
* Categories
* Payment methods
* Dates
* Financial transaction data

PostgreSQL is responsible for:

* ACID transactions
* Relational integrity
* Exact financial calculations
* SQL aggregation
* Filtering
* Pagination
* User ownership

### Users

```text
users
├── id (PK)
├── full_name
├── email (UNIQUE)
├── password_hash
├── created_at
└── updated_at
```

### Expenses

```text
expenses
├── id (PK)
├── user_id (FK → users.id)
├── amount
├── category
├── description
├── date
├── payment_method
├── notes
├── created_at
└── updated_at
```

### Budgets

```text
budgets
├── id (PK)
├── user_id (FK → users.id)
├── monthly_budget
├── month
├── year
├── created_at
└── updated_at
```

---

## ChromaDB

ChromaDB is the **vector database used by the RAG system**.

It stores vector representations of expense-related documents together with metadata used for retrieval and user isolation.

Example:

```text
Expense: 500 spent on Food
Description: Restaurant dinner
Date: 2026-08-10
```

Conceptually:

```text
PostgreSQL                     ChromaDB
──────────                     ────────
Exact transaction              Vector representation
Exact amount                   Semantic retrieval
Relational data                Expense context
SQL aggregation                Similarity search
Source of truth                RAG retrieval
```

---

# 🧠 PostgreSQL vs ChromaDB

| PostgreSQL                     | ChromaDB                      |
| ------------------------------ | ----------------------------- |
| Relational database            | Vector database               |
| Stores exact financial records | Stores vector representations |
| Users                          | Expense embeddings/documents  |
| Expenses                       | Semantic retrieval            |
| Budgets                        | RAG context                   |
| SQL queries                    | Similarity search             |
| Exact calculations             | Context retrieval             |
| Source of truth                | AI retrieval layer            |

Both databases have different responsibilities and work together in the RAG pipeline.

---

# 🤖 AI / LLM Stack

### Active LLM

**Google Gemini 2.5 Flash**

The application uses the modern:

```text
google.genai
```

SDK.

Gemini is responsible for:

* Understanding natural-language financial questions
* Processing retrieved context
* Generating personalized responses
* Providing financial insights based on the supplied context

The active AI flow is:

```text
User Query
    ↓
RAGService
    ↓
ChromaDB + PostgreSQL
    ↓
Context
    ↓
GeminiService
    ↓
Gemini 2.5 Flash
    ↓
Response
```

**Ollama/Llama 3 is not part of the current active deployment.**

---

# 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* ES6 Modules
* Chart.js
* Fetch API

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy
* REST API
* Repository Pattern
* Service Layer Architecture

### Database

* PostgreSQL
* SQLAlchemy ORM
* psycopg2
* Alembic

### Authentication

* JWT
* Argon2id password hashing
* Protected API routes

### AI / GenAI

* Google Gemini API
* Gemini 2.5 Flash
* `google.genai`
* ChromaDB
* RAG
* Vector similarity search
* Prompt guardrails

### Deployment

* Vercel — Frontend
* Render — FastAPI Backend
* Render PostgreSQL — Production Database

---

# 📁 Project Structure

```text
AI-Budget-Expense-Advisor/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── rag_service.py
│   │   │   ├── chroma_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── expense_service.py
│   │   │   ├── budget_service.py
│   │   │   └── analytics_service.py
│   │   ├── routes/
│   │   │   └── v1/
│   │   ├── middleware/
│   │   ├── prompts/
│   │   └── utils/
│   │
│   ├── alembic/
│   ├── vector_store/
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── api.js
│       ├── authManager.js
│       ├── expenseManager.js
│       ├── budgetTracker.js
│       ├── analyticsView.js
│       ├── chartManager.js
│       ├── chatWidget.js
│       └── store.js
│
├── README.md
└── .gitignore
```

---

# 🔑 Environment Variables

## Production — Render

Set these in the **Render Web Service → Environment** settings.

```text
DATABASE_URL=<Render PostgreSQL Internal Database URL>
SECRET_KEY=<your-secret-key>
GEMINI_API_KEY=<your-Gemini-API-key>
GEMINI_MODEL=gemini-2.5-flash
APP_ENV=production
DEBUG=False
```

**Never commit real credentials or API keys to GitHub.**

For `DATABASE_URL`, use the Internal Database URL provided by the Render PostgreSQL service.

---

# 🚀 Local Development

## 1. Clone Repository

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

Example:

```env
APP_NAME="AI Budget & Expense Advisor"
APP_ENV="development"
DEBUG=True

HOST="127.0.0.1"
PORT=8000

SECRET_KEY="your_jwt_secret_key_here"

DATABASE_URL="postgresql+psycopg2://expense_user:password@localhost:5432/expense_tracker"

GEMINI_API_KEY="your_google_gemini_api_key"
GEMINI_MODEL="gemini-2.5-flash"

ALLOWED_ORIGINS="http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"
```

## 5. Run Database Migrations

```bash
python -m alembic upgrade head
```

## 6. Start FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🔌 API Endpoints

| Method | Endpoint                  | Purpose              | Auth |
| ------ | ------------------------- | -------------------- | ---- |
| GET    | `/`                       | Root status          | No   |
| GET    | `/api/v1/health`          | Health check         | No   |
| POST   | `/api/v1/auth/register`   | Register user        | No   |
| POST   | `/api/v1/auth/login`      | Login                | No   |
| GET    | `/api/v1/auth/me`         | Current user         | Yes  |
| GET    | `/api/v1/expenses`        | List expenses        | Yes  |
| POST   | `/api/v1/expenses`        | Create expense       | Yes  |
| GET    | `/api/v1/expenses/{id}`   | Get expense          | Yes  |
| PUT    | `/api/v1/expenses/{id}`   | Update expense       | Yes  |
| DELETE | `/api/v1/expenses/{id}`   | Delete expense       | Yes  |
| GET    | `/api/v1/budgets/current` | Current budget       | Yes  |
| POST   | `/api/v1/budgets`         | Create budget        | Yes  |
| PUT    | `/api/v1/budgets`         | Update budget        | Yes  |
| GET    | `/api/v1/analytics`       | Financial analytics  | Yes  |
| POST   | `/api/v1/chat`            | AI financial advisor | Yes  |

---

# 🔄 Expense → RAG Synchronization

When an expense is created or modified, its corresponding vector representation is synchronized with ChromaDB.

Conceptually:

```text
Create Expense
      ↓
PostgreSQL
      ↓
Expense saved
      ↓
ChromaDB
      ↓
Vector/document synchronized
```

For updates:

```text
Update Expense
      ↓
Verify ownership
      ↓
Update PostgreSQL
      ↓
Update corresponding ChromaDB document
```

For deletion:

```text
Delete Expense
      ↓
Verify ownership
      ↓
Delete PostgreSQL record
      ↓
Remove corresponding vector
```

This keeps the retrieval layer aligned with the current expense data.

---

# 🔐 Security

The application implements:

* JWT authentication
* Argon2id password hashing
* Protected endpoints
* User ownership validation
* User-specific PostgreSQL queries
* User-specific ChromaDB metadata filtering
* CORS configuration
* Environment-based secrets
* Centralized exception handling
* Request logging

A user cannot access another user's:

* Expenses
* Budgets
* Analytics
* RAG retrieval context

---

# 🧪 Testing

The application includes testing for:

* Authentication
* Registration and login
* JWT-protected endpoints
* Expense CRUD
* Budget operations
* Analytics
* AI chat
* RAG retrieval
* User isolation
* Unauthorized access
* Invalid resources
* API responses

Run tests with:

```bash
pytest -q
```

---

# 🎤 Interview Questions

### Does your project use RAG?

> **Yes. My project implements a Retrieval-Augmented Generation pipeline. When a user asks a financial question, RAGService retrieves relevant user-specific expense information from ChromaDB using semantic similarity and combines it with exact financial statistics from PostgreSQL. This context is passed to Gemini 2.5 Flash through the `google.genai` SDK, which generates the final grounded response.**

### Why did you use RAG?

> **The LLM does not inherently know the user's private expense history. RAG allows the application to retrieve the relevant user-specific information first and provide that context to the LLM before generating the response.**

### Why PostgreSQL and ChromaDB?

> **PostgreSQL is the relational source of truth for users, expenses, budgets, and exact financial calculations. ChromaDB is used for semantic retrieval of expense context. They serve different purposes in the system.**

### Which LLM are you using?

> **The active LLM is Google Gemini 2.5 Flash, integrated using the modern `google.genai` SDK.**

### How do you prevent users from seeing each other's data?

> **The authenticated user's ID is used when querying PostgreSQL and as metadata filtering during ChromaDB retrieval. Therefore, the RAG pipeline only retrieves context belonging to the current user.**

---

# 📈 Deployment Architecture

```text
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │ Vercel Frontend │
              └────────┬────────┘
                       │ HTTPS
                       ▼
              ┌─────────────────┐
              │ Render FastAPI  │
              └───────┬─────────┘
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
     PostgreSQL   ChromaDB     Gemini API
      Render       Vector DB   Gemini 2.5 Flash
```

---

# 📸 Screenshots

Add project screenshots here:

```text
Dashboard
Expense Management
Budget Tracking
Analytics
AI Financial Advisor
```

Example:

```markdown
![Dashboard](screenshots/dashboard.png)
![Expenses](screenshots/expenses.png)
![Analytics](screenshots/analytics.png)
![AI Advisor](screenshots/ai-advisor.png)
```

---

# 📝 Resume Description

### Short Version

> Built an AI-powered Personal Finance & Expense Advisor using FastAPI, PostgreSQL, ChromaDB, and Google Gemini 2.5 Flash. Implemented a RAG pipeline that retrieves user-specific expense context and financial metrics to generate personalized AI-powered financial insights.

### Technical Version

> Developed and deployed a full-stack personal finance platform using Vanilla JavaScript, FastAPI, PostgreSQL, and ChromaDB. Implemented JWT authentication, user-level data isolation, expense-vector synchronization, semantic retrieval, and a custom RAG pipeline integrated with Gemini 2.5 Flash through the `google.genai` SDK.

---

# 🌐 Repository & Live Application

**GitHub Repository:**
[https://github.com/saumyap48/AI-Budget-Expense-Advisor](https://github.com/saumyap48/AI-Budget-Expense-Advisor)

**Live Application:**
[https://ai-budget-expense-advisor.vercel.app/](https://ai-budget-expense-advisor.vercel.app/)

**Backend API:**
[https://ai-budget-expense-advisor-4.onrender.com](https://ai-budget-expense-advisor-4.onrender.com)

**API Documentation:**
[https://ai-budget-expense-advisor-4.onrender.com/docs](https://ai-budget-expense-advisor-4.onrender.com/docs)

---

# 📜 License

MIT License
