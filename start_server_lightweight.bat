@echo off
REM Start FastAPI Server (Lightweight Mode - No Docker)

echo ============================================================
echo   RAG Financial Advisor - Lightweight Server
echo   Optimized for 4GB RAM
echo ============================================================
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_lightweight.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Virtual environment activated
echo.
echo Server Configuration:
echo   - Host: 127.0.0.1 (localhost only)
echo   - Port: 8010
echo   - Memory: ~200-300MB
echo   - No Docker required
echo   - No Redis required
echo.
echo API Endpoints:
echo   - Documentation: http://localhost:8010/docs
echo   - Health Check: http://localhost:8010/health
echo   - Upload CSV: http://localhost:8010/upload_csv
echo   - Get Insights: http://localhost:8010/insights/{user_id}
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

REM Start with minimal workers and limited resources
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --workers 1
