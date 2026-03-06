@echo off
REM Start FastAPI Server

echo ============================================================
echo   Starting RAG Financial Advisor API Server
echo ============================================================
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_and_run.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Virtual environment activated
echo Starting server on http://localhost:8010
echo.
echo API Documentation: http://localhost:8010/docs
echo Health Check: http://localhost:8010/health
echo Metrics: http://localhost:8001
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

uvicorn app.main:app --reload --port 8010
