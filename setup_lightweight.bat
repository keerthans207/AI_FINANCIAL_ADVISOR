@echo off
REM Lightweight Setup for 4GB RAM Laptop (No Docker Required)

echo ============================================================
echo   RAG Financial Advisor - Lightweight Setup
echo   Optimized for 4GB RAM - No Docker Required
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo [2/5] Virtual environment already exists, skipping...
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Install minimal dependencies
echo [4/5] Installing minimal dependencies (optimized for low RAM)...
echo This will take a few minutes...
python -m pip install --upgrade pip --quiet
pip install -r requirements-minimal.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Create data directory
if not exist "data" (
    echo [5/5] Creating data directory...
    mkdir data
    echo Data directory created!
) else (
    echo [5/5] Data directory already exists, skipping...
)
echo.

echo ============================================================
echo   Setup Complete! (Lightweight Mode)
echo ============================================================
echo.
echo System Configuration:
echo   - No Docker required
echo   - No Redis required
echo   - No Celery background tasks
echo   - Minimal RAM usage (~200-300MB)
echo   - All core features available
echo.
echo Features Available:
echo   [YES] Upload CSV and get instant RAG advice
echo   [YES] Get detailed financial insights
echo   [YES] Financial health score
echo   [YES] Personalized recommendations
echo   [NO]  Background monitoring (requires Redis/Celery)
echo.
echo Next Steps:
echo.
echo 1. Start the server:
echo    start_server_lightweight.bat
echo.
echo 2. Test the system (in a NEW window):
echo    run_test_lightweight.bat
echo.
echo 3. Or start manually:
echo    venv\Scripts\activate
echo    python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
echo.
echo ============================================================
echo.

REM Ask user what to do next
echo What would you like to do?
echo [1] Start server now
echo [2] Exit (start manually later)
echo.
set /p choice="Enter choice (1-2): "

if "%choice%"=="1" (
    echo.
    echo Starting lightweight server...
    echo Memory usage: ~200-300MB
    echo Press Ctrl+C to stop the server
    echo.
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
) else (
    echo.
    echo Setup complete! Start the server with: start_server_lightweight.bat
)

echo.
pause
