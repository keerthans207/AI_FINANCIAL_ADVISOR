@echo off
REM Run Test Script (Lightweight Mode)

echo ============================================================
echo   RAG Financial Advisor - Test (Lightweight Mode)
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
echo [IMPORTANT] Make sure the server is running!
echo.
echo If not started, open another terminal and run:
echo   start_server_lightweight.bat
echo.
echo Waiting 3 seconds before testing...
timeout /t 3 /nobreak >nul
echo.
echo ============================================================
echo.

python test_rag_system.py

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
echo.
echo Memory Usage Tips:
echo   - Close unnecessary applications
echo   - Use Task Manager to monitor RAM
echo   - Server uses ~200-300MB
echo   - Python process should stay under 500MB
echo.
pause
