# Lightweight Setup Guide (4GB RAM)

Complete guide for running the RAG Financial Advisor on a 4GB RAM laptop without Docker.

## Why Lightweight Mode?

- ✅ No Docker required (saves ~500MB RAM)
- ✅ No Redis required (saves ~50MB RAM)
- ✅ Minimal dependencies (saves ~200MB RAM)
- ✅ Total RAM usage: ~300MB (vs 1.3GB with full stack)
- ✅ Faster startup (3s vs 60s)

## Quick Start

### Windows

```cmd
# 1. Setup (one time)
setup_lightweight.bat

# 2. Start server
start_server_lightweight.bat

# 3. Test (new terminal)
run_test_lightweight.bat
```

### Linux/Mac

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements-minimal.txt

# 3. Create data directory
mkdir data

# 4. Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

# 5. Test (new terminal)
source venv/bin/activate
python test_rag_system.py
```

## What's Included

| Feature | Available |
|---------|-----------|
| Upload CSV | ✅ |
| RAG Insights | ✅ |
| Financial Health Score | ✅ |
| Savings Recommendations | ✅ |
| Investment Suggestions | ✅ |
| Action Items | ✅ |
| Background Monitoring | ❌ (requires Redis) |
| Prometheus Metrics | ❌ (optional) |

## Memory Usage

```
Python process:     ~200MB
SQLite:             ~10MB
NumPy:              ~50MB
Overhead:           ~40MB
------------------------
Total:              ~300MB
```

## API Usage

### Upload Transactions
```bash
curl -X POST "http://localhost:8010/upload_csv?user_id=1" \
  -F "file=@Sample data/enhanced_transactions.csv"
```

### Get Insights
```bash
curl "http://localhost:8010/insights/1?risk_profile=medium"
```

### Health Check
```bash
curl "http://localhost:8010/health"
```

### API Documentation
Open: http://localhost:8010/docs

## Using Python Instead of curl

Create `test_api.py`:
```python
import requests

# Upload transactions
with open("Sample data/enhanced_transactions.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8010/upload_csv?user_id=1",
        files={"file": f}
    )
    print(response.json())

# Get insights
response = requests.get("http://localhost:8010/insights/1?risk_profile=medium")
print(response.json())
```

Run: `python test_api.py`

## Troubleshooting

### Python not found
Install Python 3.11+ from https://www.python.org/downloads/
Check "Add Python to PATH" during installation.

### Cannot activate virtual environment
**PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Alternative:** Use Command Prompt instead of PowerShell.

### Port 8010 already in use
```cmd
netstat -ano | findstr :8010
taskkill /PID <PID_NUMBER> /F
```

### Out of memory
1. Close unnecessary applications
2. Use smaller CSV files (< 1000 transactions)
3. Restart Python process

### Import errors
```cmd
# Reinstall dependencies
venv\Scripts\activate
pip install -r requirements-minimal.txt --force-reinstall
```

### Database locked
```cmd
# Stop all Python processes
taskkill /F /IM python.exe

# Restart server
start_server_lightweight.bat
```

## Optimizing for 4GB RAM

### 1. Close Unnecessary Apps
Before starting:
- Close Chrome/Firefox (use Edge if needed)
- Close Slack, Discord, etc.
- Close IDE if not needed

### 2. Monitor Memory
```cmd
# Windows Task Manager
Ctrl + Shift + Esc

# Look for python.exe: Should be ~200-300MB
```

### 3. Use Smaller Datasets
- Keep last 3 months of transactions
- Delete old data periodically
- Upload monthly instead of daily

## Performance

### Startup Time
- First time: 30-60 seconds (installing packages)
- Subsequent: 3-5 seconds

### Response Times
- Upload CSV (32 transactions): 1-2 seconds
- Get insights: 0.5-1 second
- Health check: <100ms

### Concurrent Users
- Recommended: 1-2 users
- Maximum: 5 users (with delays)

## File Structure

```
ai-financial-advisor/
├── venv/                          # Virtual environment
├── app/                           # Application code
│   ├── main.py                   # FastAPI server
│   ├── rag_engine.py             # RAG system
│   ├── agents.py                 # AI agents
│   └── ...
├── data/                          # SQLite database
│   └── app.db
├── Sample data/
│   ├── sample_transactions.csv   # 6 transactions
│   └── enhanced_transactions.csv # 32 transactions
├── requirements-minimal.txt      # Minimal dependencies
├── setup_lightweight.bat         # Setup script
├── start_server_lightweight.bat  # Start server
└── run_test_lightweight.bat      # Run test
```

## System Requirements

### Minimum
- RAM: 4GB (2GB free)
- Disk: 500MB free
- CPU: Dual-core 1.5GHz
- OS: Windows 7+, Linux, macOS
- Python: 3.11+

### Recommended
- RAM: 6GB (3GB free)
- Disk: 1GB free
- CPU: Dual-core 2.0GHz
- OS: Windows 10+, Ubuntu 20.04+, macOS 11+
- Python: 3.11+

## Upgrading to Full Stack

When you get more RAM:

```cmd
# Install full requirements
pip install -r requirements.txt

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Start Redis
docker run -d -p 6379:6379 redis:latest

# Now background monitoring works!
```

## FAQ

**Q: Can I run this on 2GB RAM?**  
A: Possible but not recommended. Close all other apps.

**Q: Does it work offline?**  
A: Yes! No internet required after installation.

**Q: How much disk space needed?**  
A: ~200MB for packages, ~1MB for database.

**Q: Can I analyze large CSV files?**  
A: Yes, up to ~1000 transactions. Larger files may be slow.

**Q: Is my data secure?**  
A: Yes! Everything runs locally, no external connections.

---

**Perfect for budget laptops! 💰📊**

Back to [README.md](README.md) | See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
