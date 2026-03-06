@echo off
REM Install llama-cpp-python from pre-built wheel (no compilation needed)

echo ============================================================
echo   Installing llama-cpp-python (Pre-built Wheel)
echo   No C++ compiler required!
echo ============================================================
echo.

REM Activate venv
call venv\Scripts\activate.bat

echo Installing llama-cpp-python from pre-built wheel...
echo This may take 2-3 minutes...
echo.

REM Install from pre-built wheel (CPU-only)
pip install llama-cpp-python --prefer-binary --no-cache-dir

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Alternative: Install from GitHub releases
    echo Visit: https://github.com/abetlen/llama-cpp-python/releases
    echo Download: llama_cpp_python-*-cp311-cp311-win_amd64.whl
    echo Install: pip install downloaded_file.whl
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo Testing installation...
python -c "from llama_cpp import Llama; print('✓ llama-cpp-python installed successfully')"

if errorlevel 1 (
    echo [ERROR] Import test failed
    pause
    exit /b 1
)

echo.
echo ✓ Ready to use!
echo.
echo Next steps:
echo 1. Ensure model is in: models\phi-2.Q4_K_M.gguf
echo 2. Start server: python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
echo 3. Check status: curl http://localhost:8010/rag/status
echo.
pause
