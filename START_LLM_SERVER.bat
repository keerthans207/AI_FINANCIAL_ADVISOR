@echo off
REM Start AI Financial Advisor with LLM RAG

echo ============================================================
echo   AI Financial Advisor - LLM RAG Mode
echo   Starting server with Phi-2 (2.7B)...
echo ============================================================
echo.

REM Activate venv
call venv\Scripts\activate.bat

echo Initializing RAG system...
echo This may take 30-60 seconds on first start...
echo.
echo - Loading Phi-2 model (~1.6GB)
echo - Loading sentence-transformers
echo - Initializing FAISS vector store
echo.
echo Please wait...
echo.

REM Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

pause
