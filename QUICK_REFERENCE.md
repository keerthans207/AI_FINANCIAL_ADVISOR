# Quick Reference Card

## 🚀 Setup Commands

```cmd
# Windows
setup_lightweight.bat
start_server_lightweight.bat
run_test_lightweight.bat

# Linux/Mac
python -m venv venv && source venv/bin/activate
pip install -r requirements-minimal.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/upload_csv` | POST | Upload transactions |
| `/insights/{user_id}` | GET | Get RAG insights |
| `/advices/{user_id}` | GET | Get advice history |
| `/docs` | GET | API documentation |

## 💻 Common Commands

### Upload CSV
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

## 📊 CSV Format

```csv
date,amount,description
2025-11-01,50000,Salary November
2025-11-02,-2000,Groceries
2025-11-05,-12000,Rent
```

**Calculation:**
- Income: Sum of positive amounts
- Expense: Absolute value of negative amounts
- Surplus: Income - Expense

Example: `50000 - (2000 + 12000) = 36000`

## 🎯 Risk Profiles

| Profile | Allocation |
|---------|------------|
| Low | 60% debt, 30% balanced, 10% equity |
| Medium | 50% equity, 30% debt, 20% gold |
| High | 60% equity, 20% mid-cap, 20% debt |

## 📈 Financial Health Score

| Score | Rating | Action |
|-------|--------|--------|
| 80-100 | Excellent | Keep it up! |
| 60-79 | Good | Minor improvements |
| 40-59 | Fair | Focus on key areas |
| 0-39 | Needs Improvement | Take action now |

## 🔧 Troubleshooting

### Python not found
```cmd
# Install from python.org
# Check "Add to PATH" during install
```

### Cannot activate venv
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8010 in use
```cmd
netstat -ano | findstr :8010
taskkill /PID <PID> /F
```

### Out of memory
```cmd
# Use lightweight mode
setup_lightweight.bat
```

## 🔄 Virtual Environment

### Activate
```cmd
# Windows CMD
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### Deactivate
```cmd
deactivate
```

## 💾 Memory Usage

| Mode | RAM | Disk |
|------|-----|------|
| Lightweight | 300MB | 200MB |

## ⚡ Performance

| Metric | Time |
|--------|------|
| Startup | 3-5s |
| Response | 1-2s |
| Users | 1-2 |

## 🎓 Quick Tips

1. Start with sample data first
2. Include income transactions
3. Upload monthly to track progress
4. Try different risk profiles
5. Aim for health score 60+

## 📁 File Locations

| File | Purpose |
|------|---------|
| `data/app.db` | SQLite database |
| `Sample data/*.csv` | Sample transactions |
| `venv/` | Virtual environment |
| `.env` | Configuration |

## 🆘 Getting Help

1. Check [README.md](README.md)
2. Read [LIGHTWEIGHT_SETUP.md](LIGHTWEIGHT_SETUP.md)
3. Try lightweight mode if issues

---

**Print this for quick reference! 📄**
