@echo off
REM Run Test Script

echo ============================================================
echo   RAG Financial Advisor - Test Script
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
echo.
echo [IMPORTANT] Make sure the API server is running!
echo If not, start it with: start_server.bat
echo.
echo Press any key to continue with the test...
pause >nul
echo.
echo ============================================================
echo.

python test_rag_system.py

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
echo.
pause
