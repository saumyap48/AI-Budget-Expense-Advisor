@echo off
echo ========================================
echo  AI Budget ^& Expense Advisor - Startup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.12+ first.
    pause
    exit /b 1
)

REM Install dependencies if not already installed
echo [1/3] Checking Python dependencies...
python -m pip install -r backend/requirements.txt --quiet

REM Remind about Ollama
echo.
echo [2/3] Ollama Status Check...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama is NOT running. AI chat will use fallback mode.
    echo        To enable AI: open a new terminal and run -^> ollama run llama3
) else (
    echo [OK]   Ollama is running at http://localhost:11434
)

REM Start FastAPI Backend in background
echo.
echo [3/3] Starting FastAPI Backend on http://localhost:8000 ...
start "AI Advisor Backend" cmd /k "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul

REM Start Frontend HTTP Server
echo Starting Frontend Server on http://localhost:5500 ...
start "AI Advisor Frontend" cmd /k "python -m http.server 5500 --directory frontend"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  Application Started!
echo ========================================
echo  Frontend:  http://localhost:5500
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/api/v1/health
echo ========================================
echo.
echo Opening browser...
start http://localhost:5500

echo Press any key to exit this launcher.
pause >nul
