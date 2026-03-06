@echo off
REM Setup and Run Script for RAG Financial Advisor
REM Windows Batch Script

echo ============================================================
echo   RAG Financial Advisor - Setup and Run
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

echo [1/6] Checking Python installation...
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo [2/6] Virtual environment already exists, skipping...
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Create data directory
if not exist "data" (
    echo [5/6] Creating data directory...
    mkdir data
    echo Data directory created!
) else (
    echo [5/6] Data directory already exists, skipping...
)
echo.

REM Check if Redis is running
echo [6/6] Checking Redis...
docker ps | findstr redis >nul 2>&1
if errorlevel 1 (
    echo Redis is not running. Starting Redis container...
    docker run -d -p 6379:6379 --name redis-financial redis:latest >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not start Redis. Make sure Docker is installed.
        echo You can install Docker Desktop from: https://www.docker.com/products/docker-desktop
        echo.
        echo The API will still work, but background monitoring won't be available.
    ) else (
        echo Redis started successfully!
    )
) else (
    echo Redis is already running!
)
echo.

echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. Start the API server (in this window):
echo    uvicorn app.main:app --reload --port 8010
echo.
echo 2. Start Celery worker (in a NEW window):
echo    venv\Scripts\activate
echo    celery -A app.celery_worker.celery worker --loglevel=info -Q monitor_queue --pool=solo
echo.
echo 3. Run the test (in a NEW window):
echo    venv\Scripts\activate
echo    python test_rag_system.py
echo.
echo Or use the quick start scripts:
echo    - start_server.bat (starts API server)
echo    - start_celery.bat (starts Celery worker)
echo    - run_test.bat (runs test script)
echo.
echo ============================================================
echo.

REM Ask user what to do next
echo What would you like to do?
echo [1] Start API server now
echo [2] Run test script (requires server running in another window)
echo [3] Exit and start manually
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting API server...
    echo Press Ctrl+C to stop the server
    echo.
    uvicorn app.main:app --reload --port 8010
) else if "%choice%"=="2" (
    echo.
    echo Running test script...
    echo Make sure the API server is running in another window!
    timeout /t 3 >nul
    python test_rag_system.py
    pause
) else (
    echo.
    echo Setup complete! You can now start the services manually.
    echo See SETUP_VENV_WINDOWS.md for detailed instructions.
)

echo.
pause
