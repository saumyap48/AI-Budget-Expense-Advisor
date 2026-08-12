# 💰 AI Budget & Expense Advisor

A full-stack personal finance application that helps users **track expenses, manage monthly budgets, analyze spending patterns, and receive personalized financial advice using Retrieval-Augmented Generation (RAG)**.

The application combines **Vanilla JavaScript, FastAPI, PostgreSQL, ChromaDB, and Google Gemini 2.5 Flash** to create an AI-powered financial assistant grounded in the user's expense history and financial metrics.

---

## 🌟 Features

### 💳 Expense Management

* Create expenses
* View expense history
* Update expenses
* Delete expenses
* Search and filter expenses
* Category-based filtering
* Pagination
* Payment method tracking
* Expense notes and descriptions
* Automatic synchronization of expense data with the vector store

### 🎯 Budget Management

* Set monthly budgets
* Update existing budgets
* Track monthly spending
* Calculate remaining budget
* Calculate percentage spent
* Budget warning at 80% utilization
* Exceeded-budget alert above 100%

### 📊 Financial Analytics

* Total spending
* Transaction count
* Daily average spending
* Category-wise spending
* Spending percentages
* Daily spending trends
* Weekly and monthly spending trends
* Top spending categories
* Recent expenses
* Largest expenses
* Daily burn rate
* Projected monthly spending
* Financial health score

### 🤖 AI Financial Advisor

The application implements a **Retrieval-Augmented Generation (RAG) pipeline**.

Users can ask questions such as:

* "Where am I spending the most?"
* "How much did I spend on food?"
* "Can I reduce my monthly spending?"
* "Give me saving suggestions."
* "What are my biggest expenses?"

The system retrieves relevant expense information from **ChromaDB**, combines it with structured financial metrics from **PostgreSQL**, and sends the resulting context to **Google Gemini 2.5 Flash** to generate personalized responses.

### 🔐 Authentication & Security

* User registration
* User login
* JWT authentication
* Password hashing
* Protected API endpoints
* User-level data isolation
* User-level ChromaDB metadata filtering
* CORS configuration
* Request logging
* Centralized exception handling

---

# 🏗️ Architecture

```text
                         USER
                           │
                           ▼
              ┌──────────────────────┐
              │      Frontend        │
              │ HTML + CSS + JS      │
              │      Chart.js        │
              └──────────┬───────────┘
                         │
                    HTTP / REST
                         │
                         ▼
              ┌──────────────────────┐
              │       FastAPI        │
              │       Backend        │
              └──────────┬───────────┘
                         │
              ┌──────────┼───────────┐
              │          │           │
              ▼          ▼           ▼
        PostgreSQL   ChromaDB     JWT Auth
              │          │
              │          ▼
              │   Vector Retrieval
              │          │
              │          ▼
              │      RAG Service
              │          │
              └──────────┤
                         ▼
                Google Gemini
                  2.5 Flash
                         │
                         ▼
              Personalized AI Response
```

---

# 🔄 RAG Pipeline

The project **uses Retrieval-Augmented Generation (RAG)**.

The AI chat pipeline uses two major sources of context:

```text
User Question
      │
      ▼
POST /api/v1/chat
      │
      ▼
JWT Authentication
      │
      ▼
RAGService
      │
      ├───────────────► ChromaDB
      │                  │
      │                  ▼
      │           Semantic Retrieval
      │           Relevant Expenses
      │
      ├───────────────► PostgreSQL
      │                  │
      │                  ▼
      │          Financial Statistics
      │          Budget + Analytics
      │
      ▼
Context Construction
      │
      ▼
Prompt Template
      │
      ▼
Google Gemini 2.5 Flash
      │
      ▼
AI Financial Response
```

## 1. Vector Retrieval

ChromaDB is used to retrieve semantically relevant expense documents.

For example:

```text
User:
"What did I spend on eating outside?"

        ↓

Query
        ↓
ChromaDB similarity search
        ↓
Relevant expense documents
```

The retrieved documents are filtered by the authenticated user's `user_id`.

## 2. Structured Financial Context

The application also retrieves exact financial information through PostgreSQL and the analytics/budget services.

This can include:

* Total spending
* Category totals
* Daily average
* Budget remaining
* Monthly spending
* Spending trends
* Financial metrics

Both sources are combined by the RAG service before the request is sent to Gemini.

---

# 🧠 How RAG Works

```text
1. User asks a financial question
              ↓
2. JWT identifies the authenticated user
              ↓
3. RAGService receives the query
              ↓
4. ChromaDB performs semantic retrieval
              ↓
5. user_id filter restricts retrieval to that user
              ↓
6. PostgreSQL provides structured financial metrics
              ↓
7. RAGService combines retrieved context
              ↓
8. Prompt template is constructed
              ↓
9. Gemini 2.5 Flash receives the context
              ↓
10. Gemini generates the response
              ↓
11. Response is returned to the frontend
```

The important point is that **Gemini does not directly query the user's database**.

The application retrieves the relevant information first and then provides that context to Gemini.

---

# 🗄️ Database Architecture

The project uses two different storage systems for different purposes.

## PostgreSQL

PostgreSQL is the primary relational database.

It stores:

* Users
* Expenses
* Budgets
* Password hashes
* Dates
* Amounts
* Categories
* Payment methods
* Notes
* Relationships and constraints

### Why PostgreSQL?

PostgreSQL provides:

* ACID transactions
* Relational integrity
* Foreign keys
* Unique constraints
* Exact financial calculations
* SQL aggregation
* Filtering
* Pagination
* Indexed queries

---

# 🔎 ChromaDB

ChromaDB is the vector database used by the RAG system.

Expense information is converted into document text and indexed for semantic retrieval.

Example:

```text
Expense: $500 on Food (Restaurant dinner) on 2026-08-10.
Notes: Dinner with friends.
```

Associated metadata includes:

```text
expense_id
user_id
category
amount
date
description
```

### Why ChromaDB?

PostgreSQL is useful for exact structured queries such as:

```sql
SELECT SUM(amount)
FROM expenses
WHERE category = 'Food';
```

ChromaDB is useful for semantic queries expressed naturally by the user, such as:

```text
"Show me expenses related to eating outside."
```

The vector search helps retrieve relevant expense documents based on semantic similarity.

---

# 🔐 Multi-User RAG Security

Each expense vector contains a `user_id`.

During retrieval, ChromaDB applies a user-level metadata filter:

```text
user_id = current_user.id
```

Therefore:

```text
User A
   ↓
Only User A's expense vectors

User B
   ↓
Only User B's expense vectors
```

This prevents one user's expense information from being included in another user's AI retrieval context.

---

# 🤖 LLM

## Active LLM

**Google Gemini 2.5 Flash**

Gemini is responsible for:

* Understanding the user's financial question
* Processing retrieved financial context
* Generating natural-language responses
* Providing personalized financial insights
* Providing saving suggestions

The Gemini API is accessed through:

```text
GeminiService
```

which is invoked by:

```text
RAGService
```

The active AI flow is:

```text
User Query
    ↓
RAGService
    ↓
ChromaDB + PostgreSQL
    ↓
Context Construction
    ↓
GeminiService
    ↓
Gemini 2.5 Flash
    ↓
Final Response
```

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* ES6 Modules
* Chart.js
* Fetch API
* LocalStorage

The frontend does not use React, Vue, or Angular.

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic v2
* SQLAlchemy
* REST API
* Repository Pattern
* Service Layer Architecture

## Database

* PostgreSQL
* SQLAlchemy ORM
* psycopg2
* Alembic

## Authentication

* JWT
* PyJWT
* Passlib
* Password hashing

## AI / GenAI

* Google Gemini API
* Gemini 2.5 Flash
* ChromaDB
* RAG
* Vector similarity search
* Prompt templates

## Testing

* Pytest
* FastAPI TestClient
* API tests
* Authentication tests
* End-to-end tests
* Multi-user isolation tests
* RAG tests

---

# 📁 Project Structure

```text
AI-Budget-Expense-Advisor/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── expense.py
│   │   │   └── budget.py
│   │
│   │   ├── schemas/
│   │
│   │   ├── repositories/
│   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── expense_service.py
│   │   │   ├── budget_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── chroma_service.py
│   │   │   └── gemini_service.py
│   │
│   │   ├── routes/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── expenses.py
│   │   │       ├── budgets.py
│   │   │       ├── analytics.py
│   │   │       ├── chat.py
│   │   │       └── health.py
│   │
│   │   ├── middleware/
│   │   ├── prompts/
│   │   └── utils/
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── vector_store/
│   │   └── chroma_db/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   ├── test_api.py
│   ├── test_e2e.py
│   ├── test_auth_e2e.py
│   └── test_ai.py
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
├── README.md
└── .gitignore
```

---

# 🔑 Authentication Flow

## Registration

```text
Client
  ↓
POST /api/v1/auth/register
  ↓
Pydantic Validation
  ↓
Check Existing Email
  ↓
Hash Password
  ↓
Store User in PostgreSQL
  ↓
Generate JWT
  ↓
Return Access Token
```

## Login

```text
Client
  ↓
POST /api/v1/auth/login
  ↓
Find User
  ↓
Verify Password
  ↓
Generate JWT
  ↓
Return Access Token
```

## Protected Request

```text
Authorization: Bearer <JWT>
              ↓
       JWT Validation
              ↓
        User Identification
              ↓
      User-Specific Resource
```

---

# 💸 Expense Flow

## Create Expense

```text
POST /api/v1/expenses
        ↓
Pydantic Validation
        ↓
Input Validation
        ↓
PostgreSQL
        ↓
Create Expense Record
        ↓
ChromaDB
        ↓
Create / Update Expense Vector
        ↓
Return Response
```

## Update Expense

```text
PUT /api/v1/expenses/{id}
        ↓
Verify Ownership
        ↓
Update PostgreSQL
        ↓
Update ChromaDB Vector
        ↓
Return Updated Expense
```

## Delete Expense

```text
DELETE /api/v1/expenses/{id}
        ↓
Verify Ownership
        ↓
Delete PostgreSQL Record
        ↓
Delete Corresponding Vector
        ↓
Return Success
```

---

# 📊 Analytics Flow

```text
Frontend
   ↓
GET /api/v1/analytics
   ↓
JWT Authentication
   ↓
AnalyticsService
   ↓
PostgreSQL Aggregate Queries
   ↓
SUM / COUNT / GROUP BY
   ↓
Python Calculations
   ↓
Financial Analytics Response
   ↓
Chart.js
```

---

# 🎯 Budget Flow

```text
Set Budget
    ↓
PostgreSQL
    ↓
Monthly Budget

Get Current Budget
    ↓
Calculate Monthly Expenses
    ↓
Calculate Remaining Balance
    ↓
Calculate Percentage Spent
    ↓
Determine Alert Level
```

Alert levels:

```text
< 80%       → Normal
80% - 100%  → Warning
> 100%      → Exceeded
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

# 🧪 Testing

The project includes automated testing for:

* Authentication
* JWT validation
* Expense CRUD
* Budget operations
* Analytics
* AI chat
* RAG retrieval
* Multi-user isolation
* Unauthorized requests
* Invalid input
* Resource ownership
* API endpoint behavior

Run the test suite with:

```bash
pytest -q
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

API documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## 7. Start Frontend

Serve the frontend using a local static server:

```bash
cd frontend
python -m http.server 8080
```

Then open:

```text
http://127.0.0.1:8080
```

---

# 🧩 Architecture & Design Patterns

The backend follows a layered architecture:

```text
Routes
  ↓
Services
  ↓
Repositories
  ↓
Database
```

The AI pipeline follows:

```text
Routes
  ↓
RAGService
  ├── ChromaService
  ├── AnalyticsService
  ├── BudgetService
  └── GeminiService
```

Architectural concepts used:

* Repository Pattern
* Service Layer
* Dependency Injection
* REST API
* Pydantic Schemas / DTOs
* JWT Authentication
* Middleware
* RAG Architecture
* Vector Search
* Separation of Concerns

---

# 🔒 Security

The application implements:

* JWT-based authentication
* Password hashing
* Protected endpoints
* User ownership checks
* User-specific PostgreSQL queries
* User-specific ChromaDB filtering
* CORS configuration
* Environment-based secrets
* Centralized error handling
* Request logging

A user cannot access another user's:

* Expenses
* Budgets
* Analytics
* AI retrieval context

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
