@echo off
REM Setup script for LLM RAG mode (4GB RAM, CPU-only)

echo ============================================================
echo   AI Financial Advisor - LLM RAG Setup
echo   Phi-2 (2.7B) + FAISS + sentence-transformers
echo   Optimized for 4GB RAM, CPU-only
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version
echo.

REM Create venv
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/5] Virtual environment exists
)
echo.

REM Activate venv
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing LLM RAG dependencies...
echo This will take 5-10 minutes...
echo.
pip install --upgrade pip -q
pip install -r requirements-llm.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

REM Create directories
if not exist "data" mkdir data
if not exist "models" mkdir models

echo [5/5] Checking for Phi-2 model...
if exist "models\phi-2.Q4_K_M.gguf" (
    echo Model found: models\phi-2.Q4_K_M.gguf
) else (
    echo Model not found!
    echo.
    echo To download Phi-2 model (~1.6GB):
    echo   python download_models.py
    echo.
    echo Or download manually from:
    echo   https://huggingface.co/TheBloke/phi-2-GGUF
    echo   File: phi-2.Q4_K_M.gguf
    echo   Place in: models\phi-2.Q4_K_M.gguf
)
echo.

echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo System Configuration:
echo   - LLM: Phi-2 (2.7B) Q4_K_M GGUF
echo   - Embeddings: all-MiniLM-L6-v2
echo   - Vector Store: FAISS (CPU)
echo   - RAM Usage: ~1.5GB
echo   - Mode: CPU-only, no GPU
echo.
echo Next Steps:
echo.
echo 1. Download model (if not done):
echo    python download_models.py
echo.
echo 2. Start server:
echo    venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
echo.
echo 3. Check RAG status:
echo    curl http://localhost:8010/rag/status
echo.
echo 4. Test with sample data:
echo    python test_rag_system.py
echo.
echo ============================================================
pause
