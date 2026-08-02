# AI Budget & Expense Advisor (Full Stack + Gemini AI + RAG)

A production-grade personal finance web application where users can manage daily expenses, set and track monthly budgets, visualize spending analytics via interactive charts, and consult an AI assistant powered by **Retrieval-Augmented Generation (RAG)** using **Google Gemini API** and **ChromaDB**.

---

## 🌟 Features

- 💳 **Full Expense Lifecycle (CRUD)**: Record, update, search, filter by category, and delete transactions with instant state synchronization.
- 🎯 **Monthly Budgeting & Alerts**: Dynamic budget utilization tracking with visual warnings when spending exceeds 80% and alerts when over 100%.
- 📊 **Interactive Data Analytics**: Visual dashboards powered by Chart.js featuring daily spending trend lines, category distribution doughnut charts, daily average calculations, and top spending categories.
- 🤖 **Gemini AI Financial Assistant**: Grounded AI chatbot answering questions based **strictly on your personal expense data** using ChromaDB vector search and Google Gemini (`gemini-2.5-flash`).
- 🛡️ **Zero-Hallucination RAG Pipeline**: Strict prompt guardrails prevent the AI from generating unverified or hallucinated financial numbers.
- ☁️ **Cloud AI, Private Data**: Your expense data never leaves your machine — only the query prompt is sent to Gemini's API.

---

## 🏗️ Architecture Overview

```
User (Browser) <---> Vanilla JS Frontend (Fetch API + Chart.js)
                             │
                     FastAPI Backend (REST API)
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   SQLite DB             ChromaDB            Gemini API
(Expenses & Budget)  (Vector Database)  (gemini-2.5-flash)
```

---

## 📁 Folder Structure

```
AI-Budget-Expense-Advisor/
├── backend/
│   ├── app/
│   │   ├── main.py                     # App factory & FastAPI startup
│   │   ├── core/                       # Configuration, DB engine, logger & security
│   │   ├── models/                     # SQLAlchemy ORM Models (Expense, Budget)
│   │   ├── schemas/                    # Pydantic request/response validation DTOs
│   │   ├── repositories/               # Repository pattern for database abstraction
│   │   ├── services/                   # Business logic, ChromaDB & RAG orchestrator
│   │   │   └── gemini_service.py       # Google Gemini API integration
│   │   ├── routes/                     # Versioned REST API endpoints (/api/v1)
│   │   ├── middleware/                 # Request logging & error translation
│   │   ├── prompts/                    # Financial prompt templates
│   │   └── utils/                      # Datetime and text document builders
│   ├── data/                           # SQLite database storage (finance.db)
│   ├── vector_store/                   # Persistent ChromaDB index storage
│   ├── logs/                           # Operational, AI, and error log files
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                            # ⚠️ Not committed — add your GEMINI_API_KEY here
│
├── frontend/
│   ├── index.html                      # Single Page Application HTML
│   ├── css/                            # Glassmorphism dark mode design system
│   └── js/                             # ES6 modular components (charts, chat, budget)
│
├── README.md
└── .gitignore
```

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla Glassmorphism), JavaScript (ES6 Modules), Chart.js
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, SQLite, Pydantic v2
- **AI & RAG**: Google Gemini API (`gemini-2.5-flash`), ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`)

---

## 🚀 Setup & Execution Guide

### Prerequisites
1. **Python 3.12+** installed.
2. A **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey).

### Step 1: Configure Environment
Copy `.env.example` to `.env` inside the `backend/` folder and add your Gemini API key:
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env`:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-2.5-flash"
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

### Step 4: Open Frontend Application
Open `frontend/index.html` in your web browser (or serve using VS Code Live Server / `python -m http.server 5500` inside `frontend/`).

---

## 📝 Resume Project Highlights

> **Built an AI-powered Personal Finance & Expense Advisor using FastAPI, SQLAlchemy, SQLite, ChromaDB, Sentence-Transformers, Google Gemini API, and Chart.js. Architected a layered system incorporating the Repository Pattern, versioned REST APIs, automatic vector sync on database mutations, and RAG metadata filtering with zero-hallucination guardrails.**

---

## 📸 Screenshots

*(Add screenshots of Dashboard, Expense Table, Budget Ring, and AI Chat UI here)*

---

## 📄 License

MIT License
