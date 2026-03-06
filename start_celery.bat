@echo off
REM Start Celery Worker

echo ============================================================
echo   Starting Celery Worker for Background Tasks
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
echo Starting Celery worker...
echo.
echo Press Ctrl+C to stop the worker
echo.
echo ============================================================
echo.

celery -A app.celery_worker.celery worker --loglevel=info -Q monitor_queue --pool=solo
