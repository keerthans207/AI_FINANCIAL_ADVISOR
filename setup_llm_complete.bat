@echo off
REM Complete LLM RAG Setup (handles llama-cpp-python installation)

echo ============================================================
echo   AI Financial Advisor - Complete LLM Setup
echo   Phi-2 (2.7B) + FAISS + sentence-transformers
echo   Optimized for 4GB RAM, CPU-only
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Python found
python --version
echo.

REM Create venv
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/6] Virtual environment exists
)
echo.

REM Activate venv
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install base dependencies (without llama-cpp-python)
echo [4/6] Installing base dependencies...
echo This will take 5-10 minutes...
echo.
pip install --upgrade pip -q
pip install -r requirements-llm.txt -q

if errorlevel 1 (
    echo [WARNING] Some packages may have failed
    echo Continuing with llama-cpp-python installation...
)
echo Base dependencies installed!
echo.

REM Install llama-cpp-python from pre-built wheel
echo [5/6] Installing llama-cpp-python (pre-built wheel)...
echo This avoids C++ compilation...
echo.

pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

if errorlevel 1 (
    echo.
    echo [WARNING] Pre-built wheel installation failed
    echo.
    echo MANUAL INSTALLATION REQUIRED:
    echo 1. Visit: https://github.com/abetlen/llama-cpp-python/releases
    echo 2. Download: llama_cpp_python-*-cp311-cp311-win_amd64.whl
    echo 3. Install: pip install path\to\downloaded_file.whl
    echo.
    echo OR use alternative method:
    echo pip install llama-cpp-python --prefer-binary
    echo.
    set LLAMA_INSTALLED=0
) else (
    echo ✓ llama-cpp-python installed successfully!
    set LLAMA_INSTALLED=1
)
echo.

REM Create directories
if not exist "data" mkdir data
if not exist "models" mkdir models

REM Check for model
echo [6/6] Checking for Phi-2 model...
if exist "models\phi-2.Q4_K_M.gguf" (
    echo ✓ Model found: models\phi-2.Q4_K_M.gguf
    for %%A in ("models\phi-2.Q4_K_M.gguf") do echo   Size: %%~zA bytes
    set MODEL_FOUND=1
) else (
    echo ✗ Model not found!
    echo.
    echo Please ensure phi-2.Q4_K_M.gguf is in the models\ folder
    echo If you have it in the project root, run:
    echo   move phi-2.Q4_K_M.gguf models\
    echo.
    set MODEL_FOUND=0
)
echo.

echo ============================================================
echo   Setup Status
echo ============================================================
echo.
if "%LLAMA_INSTALLED%"=="1" (
    echo ✓ llama-cpp-python: Installed
) else (
    echo ✗ llama-cpp-python: NEEDS MANUAL INSTALLATION
)

if "%MODEL_FOUND%"=="1" (
    echo ✓ Phi-2 Model: Found
) else (
    echo ✗ Phi-2 Model: Not found
)
echo.

if "%LLAMA_INSTALLED%"=="1" if "%MODEL_FOUND%"=="1" (
    echo ============================================================
    echo   Ready to Start!
    echo ============================================================
    echo.
    echo Start server:
    echo   python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
    echo.
    echo Check RAG status:
    echo   curl http://localhost:8010/rag/status
    echo.
    echo Test with sample data:
    echo   curl -X POST "http://localhost:8010/upload_csv?user_id=1" -F "file=@Sample data/enhanced_transactions.csv"
    echo.
) else (
    echo ============================================================
    echo   Action Required
    echo ============================================================
    echo.
    if not "%LLAMA_INSTALLED%"=="1" (
        echo 1. Install llama-cpp-python manually
        echo    See instructions above
        echo.
    )
    if not "%MODEL_FOUND%"=="1" (
        echo 2. Place Phi-2 model in models\ folder
        echo    File: phi-2.Q4_K_M.gguf
        echo.
    )
)

echo ============================================================
pause
