# Installing llama-cpp-python on Windows

The `llama-cpp-python` package requires C++ compilation on Windows. Here are three methods to install it:

## Method 1: Pre-built Wheel (Recommended)

```cmd
# Activate virtual environment
venv\Scripts\activate

# Install from pre-built wheel repository
pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

## Method 2: Download Pre-built Wheel

1. Visit: https://github.com/abetlen/llama-cpp-python/releases
2. Download the wheel for your Python version:
   - For Python 3.11: `llama_cpp_python-*-cp311-cp311-win_amd64.whl`
   - For Python 3.10: `llama_cpp_python-*-cp310-cp310-win_amd64.whl`
3. Install the downloaded wheel:
   ```cmd
   pip install path\to\llama_cpp_python-*-cp311-cp311-win_amd64.whl
   ```

## Method 3: Install with Visual Studio Build Tools

If you want to compile from source:

1. Install Visual Studio Build Tools:
   - Download: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"
   - Install (requires ~6GB disk space)

2. Install llama-cpp-python:
   ```cmd
   pip install llama-cpp-python
   ```

## Verify Installation

```cmd
python -c "from llama_cpp import Llama; print('Success!')"
```

If you see "Success!", the installation worked!

## Troubleshooting

### Error: "CMAKE_C_COMPILER not set"
**Solution**: Use Method 1 or 2 (pre-built wheels)

### Error: "No module named 'llama_cpp'"
**Solution**: Make sure virtual environment is activated:
```cmd
venv\Scripts\activate
```

### Error: "DLL load failed"
**Solution**: Install Visual C++ Redistributable:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

## Alternative: Run Without LLM

If you can't install llama-cpp-python, the system will automatically fall back to rule-based advice:

```cmd
# Install minimal dependencies
pip install -r requirements-minimal.txt

# Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

The system will work but use rule-based advice instead of LLM-generated advice.

## Quick Test

After installation, test the complete system:

```cmd
# 1. Check if model exists
dir models\phi-2.Q4_K_M.gguf

# 2. Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

# 3. Check RAG status (in new terminal)
curl http://localhost:8010/rag/status
```

Expected response:
```json
{
  "status": "operational",
  "details": {
    "initialized": true,
    "embedding_model_loaded": true,
    "llm_model_loaded": true
  }
}
```

---

**Need help? Check the logs for detailed error messages.**
