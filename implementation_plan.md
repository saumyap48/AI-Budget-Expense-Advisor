# Production Architecture Blueprint - AI Budget & Expense Advisor

Comprehensive software architecture and technical specification document for the **AI Budget & Expense Advisor** application, designed to meet production standards, portfolio excellence, and technical interview benchmarks while operating 100% locally.

---

## 1. Improved Folder Structure

```
AI-Budget-Expense-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                     # App factory (`create_app`), middleware setup, router mount
│   │   ├── core/                       # Core configuration, infrastructure & security
│   │   │   ├── config.py               # Pydantic BaseSettings (env loading & validation)
│   │   │   ├── database.py             # SQLAlchemy engine, session maker, WAL pragma setup
│   │   │   ├── logging.py              # Centralized multi-handler logger configuration
│   │   │   ├── security.py             # Security helper functions & CORS setup
│   │   │   └── exceptions.py           # Domain exception classes & HTTP mappings
│   │   ├── models/                     # SQLAlchemy ORM Data Entities
│   │   │   ├── base.py                 # Base model with common fields (id, created_at, updated_at)
│   │   │   ├── expense.py              # Expense entity with indexes & constraints
│   │   │   └── budget.py               # Budget entity with unique constraints
│   │   ├── schemas/                    # Pydantic Request/Response DTOs
│   │   │   ├── common.py               # Standard Response wrapper & Pagination metadata
│   │   │   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseRead, ExpenseFilter
│   │   │   ├── budget.py               # BudgetCreate, BudgetRead, BudgetStatus
│   │   │   ├── analytics.py            # FinancialMetrics, TrendPoint, CategoryBreakdown
│   │   │   └── chat.py                 # ChatRequest, ChatResponse, ContextDocument
│   │   ├── repositories/               # Data Access Layer (Repository Pattern)
│   │   │   ├── base.py                 # Generic BaseRepository[T] with common CRUD
│   │   │   ├── expense_repository.py   # Specialized SQL queries & date aggregation math
│   │   │   └── budget_repository.py    # Budget lookup & month/year query methods
│   │   ├── services/                   # Business & Domain Logic Layer
│   │   │   ├── expense_service.py      # Expense lifecycle logic + ChromaDB vector sync
│   │   │   ├── budget_service.py       # Budget utilization calculations & alert triggers
│   │   │   ├── analytics_service.py    # Trend computations, burn rate & health score math
│   │   │   ├── chroma_service.py       # Vector DB collection management & similarity query
│   │   │   ├── ollama_service.py       # Ollama REST client (timeout, retry & fallback)
│   │   │   └── rag_service.py          # RAG Orchestrator (Query ➔ Context ➔ Prompt ➔ LLM)
│   │   ├── routes/                     # REST API Controllers (Versioned `/api/v1`)
│   │   │   ├── api_v1.py               # Router aggregator for v1 endpoints
│   │   │   └── v1/
│   │   │       ├── expenses.py         # Endpoints for `/api/v1/expenses`
│   │   │       ├── budgets.py          # Endpoints for `/api/v1/budgets`
│   │   │       ├── analytics.py        # Endpoints for `/api/v1/analytics`
│   │   │       ├── chat.py             # Endpoints for `/api/v1/chat`
│   │   │       └── health.py           # Endpoints for `/api/v1/health`
│   │   ├── middleware/                 # Custom ASGI Middlewares
│   │   │   ├── logging_middleware.py   # Request timer & audit request logger
│   │   │   └── error_handler.py        # Global unhandled exception translator
│   │   ├── prompts/                    # Specialized System & Advisory Prompt Engines
│   │   │   ├── system_prompt.py        # Core persona & zero-hallucination guardrails
│   │   │   ├── expense_prompt.py       # Expense analysis prompt templates
│   │   │   ├── analytics_prompt.py     # Analytics & spending breakdown prompt templates
│   │   │   ├── budget_prompt.py        # Budget utilization & overspend prompt templates
│   │   │   └── saving_tips_prompt.py   # Financial health & saving recommendation templates
│   │   └── utils/                      # Pure Helper Utilities
│   │       ├── datetime_utils.py       # ISO date formatting, week/month range generators
│   │       └── text_utils.py           # Document string builders & prompt formatters
│   ├── logs/                           # Log file directory
│   │   ├── app.log
│   │   ├── error.log
│   │   ├── ai.log
│   │   └── request.log
│   ├── data/                           # Local SQLite storage (`finance.db`)
│   ├── vector_store/                   # Persistent ChromaDB vector index storage
│   ├── tests/                          # Automated Unit & Integration Test Suite
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   ├── index.html                      # SPA entry container
│   ├── css/
│   │   ├── style.css                   # Core tokens, color palette, dark mode variables
│   │   ├── dashboard.css               # Cards, grid layout, statistical panels & modals
│   │   └── chat.css                    # AI Assistant drawer & interactive chat UI
│   ├── js/
│   │   ├── config.js                   # API endpoints & application constants
│   │   ├── services/
│   │   │   ├── api.js                  # Fetch wrapper with interceptors & error handler
│   │   │   └── store.js                # Central reactive state management store
│   │   ├── components/
│   │   │   ├── expenseManager.js       # Expense table CRUD modal & pagination
│   │   │   ├── budgetTracker.js        # Budget circular ring & status badge
│   │   │   ├── analyticsView.js        # Metrics overview cards & statistical summaries
│   │   │   ├── chartManager.js         # Chart.js initialization & dynamic data updates
│   │   │   └── chatWidget.js           # AI Assistant chat window & prompt pills
│   │   └── app.js                      # Main application entry point & event bus
│   └── assets/                         # SVG icons, favicon & visual graphics
│
├── README.md                           # Documentation, setup & setup architecture
├── LICENSE                             # Open source license
└── .gitignore                          # Git ignore rules
```

---

## 2. Architecture Diagram

```
                             ┌───────────────────────────────┐
                             │       User Web Browser        │
                             │  (HTML5 / CSS3 / Vanilla JS)  │
                             └───────────────┬───────────────┘
                                             │ REST API (Fetch / JSON)
                                             ▼
                             ┌───────────────────────────────┐
                             │    FastAPI Application v1     │
                             │ (CORS / Middlewares / Router) │
                             └───────────────┬───────────────┘
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │                     │                     │
                       ▼                     ▼                     ▼
             ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
             │  Expense Service  │ │ Analytics Service │ │    RAG Service    │
             └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
                       │                     │                     │
        ┌──────────────┴──────────────┐      │           ┌─────────┴─────────┐
        ▼                             ▼      ▼           ▼                   ▼
┌──────────────┐              ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
│  SQLAlchemy  │              │  ChromaDB    │    │ Vector Query │   │ Local Ollama │
│  Repository  │              │ Vector Store │    │ Context Docs │   │ (Llama 3 LLM)│
└───────┬──────┘              └───────┬──────┘    └───────┬──────┘   └───────┬──────┘
        │                             │                   │                  │
        ▼                             ▼                   └────────┬─────────┘
┌──────────────┐              ┌──────────────┐                     │
│  SQLite DB   │              │ Embeddings   │                     ▼
│(finance.db)  │              │(all-MiniLM)  │            ┌─────────────────┐
└──────────────┘              └──────────────┘            │ Grounded Answer │
                                                          └─────────────────┘
```

---

## 3. Improved Backend Architecture

### App Factory Pattern (`create_app`)
* Initializes FastAPI app dynamically using application configuration.
* Registers custom CORS policies, logging middleware, global error handling middlewares, and lifecycle event handlers (e.g. SQLite WAL pragma init and ChromaDB singleton setup).

### Clean Layered Architecture (SOLID Principles)
1. **Routes Layer (`routes/v1/`)**: Pure controller layer responsible ONLY for request parsing, query parameter validation, status code mapping, and response serialization using DTOs.
2. **Service Layer (`services/`)**: Implements business rules (e.g., calculation of budget percentage spent, triggering budget overspend warnings, and sync of modified expenses into vector store).
3. **Repository Layer (`repositories/`)**: Implements data access abstraction over SQLAlchemy. Routes and Services never execute direct raw database queries; they interact with `ExpenseRepository` and `BudgetRepository`.

### DTO Mapping & Standard Response Wrapper (`schemas/common.py`)
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "error": null,
  "meta": {
    "page": 1,
    "limit": 20,
    "total_records": 150,
    "total_pages": 8
  }
}
```

---

## 4. Improved Database Schema & Indexing

### Table 1: `expenses`
* `id`: INTEGER, Primary Key, Auto Increment
* `amount`: NUMERIC(10, 2), NOT NULL, Check: `amount > 0`
* `category`: VARCHAR(50), NOT NULL, Indexed
* `description`: VARCHAR(255), NOT NULL
* `date`: DATE, NOT NULL, Indexed
* `payment_method`: VARCHAR(30), Default: `'Cash'` (Options: `'Cash'`, `'Credit Card'`, `'Debit Card'`, `'UPI'`, `'Bank Transfer'`)
* `notes`: TEXT, Nullable
* `created_at`: DATETIME, Default: CURRENT_TIMESTAMP
* `updated_at`: DATETIME, Default: CURRENT_TIMESTAMP

> **Database Indexes & Constraints**:
> * Composite Index: `idx_expense_date_category (date, category)` for high-performance period/category filtering.
> * Check Constraint: `check_positive_expense_amount (amount > 0)` to guarantee financial data validity at storage layer.

### Table 2: `budgets`
* `id`: INTEGER, Primary Key, Auto Increment
* `monthly_budget`: NUMERIC(10, 2), NOT NULL, Check: `monthly_budget > 0`
* `month`: INTEGER, NOT NULL, Check: `month BETWEEN 1 AND 12`
* `year`: INTEGER, NOT NULL, Check: `year >= 2000`
* `created_at`: DATETIME, Default: CURRENT_TIMESTAMP
* `updated_at`: DATETIME, Default: CURRENT_TIMESTAMP

> **Database Constraints**:
> * Unique Constraint: `uq_budget_month_year (month, year)` enforcing exactly 1 budget configuration per calendar month.

---

## 5. Improved API Design (`/api/v1`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/expenses` | List expenses with pagination (`page`, `limit`), sorting (`sort_by`, `order`), filtering (`category`, `start_date`, `end_date`), search (`q`) |
| `POST` | `/api/v1/expenses` | Create new expense, validate input, and sync vector index |
| `GET` | `/api/v1/expenses/{id}` | Retrieve expense by ID |
| `PUT` | `/api/v1/expenses/{id}` | Update existing expense and update ChromaDB vector document |
| `DELETE` | `/api/v1/expenses/{id}` | Delete expense and purge vector document |
| `GET` | `/api/v1/budgets/current` | Get current active budget utilization & alert status |
| `POST` | `/api/v1/budgets` | Set or update monthly budget |
| `GET` | `/api/v1/analytics` | Retrieve comprehensive metrics (totals, averages, trends, top spenders, health score) |
| `POST` | `/api/v1/chat` | AI RAG query endpoint with context retrieval and Llama 3 generation |
| `GET` | `/api/v1/health` | Comprehensive health check (SQLite DB check + Ollama service check) |

---

## 6. Improved Prompt Architecture

Rather than a single prompt file, prompts are split by specialized domain intent:

1. **`system_prompt.py`**: Defines core persona, strict zero-hallucination boundary rules, and JSON formatting requirements.
2. **`expense_prompt.py`**: Specialized template for analyzing specific transaction trends and vendor spending.
3. **`analytics_prompt.py`**: Formats macro financial metrics (Total spent, Daily average, Category percentage distribution) into structured context.
4. **`budget_prompt.py`**: Evaluates budget burn rate and generates actionable warning alerts when spending exceeds 80% or 100%.
5. **`saving_tips_prompt.py`**: Formats non-hallucinated practical savings suggestions derived from top spending categories.

---

## 7. Improved RAG Architecture

```
[ User Query ]
      │
      ▼
[ Query Intent & Metadata Extractor ] ➔ Extract category/date filters
      │
      ▼
[ ChromaDB Hybrid Vector Search ] ➔ Top-K=5 search + distance thresholding (< 0.45)
      │
      ▼
[ Context Assembler ] ➔ Format retrieved documents + inject SQL analytical aggregates
      │
      ▼
[ Prompt Construction ] ➔ System Prompt + Guardrails + Context + User Question
      │
      ▼
[ Ollama Llama 3 LLM ] ➔ Streamed or JSON answer generation
      │
      ▼
[ Output Guardrail ] ➔ Validate response contains no unverified numerical values
```

---

## 8. Analytics & Financial Metrics Suite

1. **Total Expenses**: Sum of all expenses in selected date window.
2. **Daily Average**: Total expenses ÷ number of active days in period.
3. **Budget Utilization**: `(Total Monthly Spent / Monthly Budget) * 100`.
4. **Budget Burn Rate**: Average daily spent vs. remaining daily allowance to last until end of month.
5. **Category Breakdown**: Percentage distribution per category (`Food: 35%`, `Bills: 25%`, etc.).
6. **Highest & Lowest Spending Category**: Dynamic ranking of top expense categories.
7. **Daily / Weekly / Monthly Trends**: Grouped time-series lists for Chart.js rendering.
8. **Top 5 Largest Expenses**: Ranked transaction list highlighting high-value spending.
9. **Financial Health Score**: Composite 0-100 rating derived from budget utilization, daily consistency, and savings margin.

---

## 9. Logging & Security Strategy

### Logging (`logs/`)
* Standardized JSON log output.
* Dedicated log handlers: `app.log` (general operational logs), `error.log` (stack traces & exception logs), `ai.log` (prompts, retrieval scores, LLM response latency), `request.log` (HTTP methods, paths, status codes, execution duration in ms).

### Security Measures
* **SQL Injection**: Prevented using SQLAlchemy ORM parametrized queries.
* **XSS Prevention**: Frontend renders dynamic content using DOM `textContent` and HTML escaping.
* **Input Validation**: Pydantic v2 validation rules on all incoming payloads.
* **CORS Limits**: Strict local origin white-listing (`http://127.0.0.1:5500`, `http://localhost:8000`).

---

## 10. Performance Strategy

* **SQLite WAL Mode**: Enabled via database engine listeners (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`).
* **ChromaDB Connection Pooling**: App lifespan singleton manager avoids re-loading embedding models on every HTTP request.
* **Chart.js Canvas Updates**: Charts update in-place using `chart.update('none')` without recreating canvas objects.

---

## 11. Deployment Strategy

* Local command runner scripts (`run_app.bat` / `run_app.sh`).
* Automatic launch sequence:
  1. Check Python virtual environment & dependencies.
  2. Verify Ollama service is running (`http://localhost:11434/api/tags`). If missing, inform user to run `ollama run llama3`.
  3. Start FastAPI server via Uvicorn (`uvicorn backend.app.main:app --port 8000`).
  4. Serve static frontend assets via FastAPI or local browser.

---

## 12. Future Roadmap (Post-MVP)

* **Phase 2**: JWT Authentication & multi-user isolate database schemas.
* **Phase 3**: PostgreSQL migration & Redis cache layer for high-frequency queries.
* **Phase 4**: Receipt OCR scanning using Tesseract / local vision models.
* **Phase 5**: CSV / PDF expense import & export reporting.

---

## 13. Production Readiness Checklist

- [x] Application Factory pattern implemented (`main.py`)
- [x] Versioned API routes under `/api/v1`
- [x] Repository pattern separating database operations from business logic
- [x] Composite database indexes on frequently queried fields (`date`, `category`)
- [x] Strict DB constraints (Check constraints & Unique budget constraints)
- [x] Modular prompt engineering architecture (`system_prompt`, `expense_prompt`, etc.)
- [x] Zero-hallucination RAG pipeline with similarity distance thresholding
- [x] Ollama client fallback & timeout handling
- [x] Structured JSON logging across application, requests, and AI pipelines
- [x] Reactive component-based ES6 frontend architecture
