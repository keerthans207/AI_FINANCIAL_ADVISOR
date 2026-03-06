# RAG-Powered AI Financial Advisor 💰🤖

An intelligent financial advisory system with **LOCAL LLM** (Phi-2) using Retrieval-Augmented Generation (RAG) to provide personalized insights based on your transaction data.

> **🚀 NEW: Local LLM Mode with Phi-2 (2.7B)**  
> **💻 Optimized for 4GB RAM, CPU-only, no GPU required!**

## 🌟 Features

### Core Features
- 📊 **Financial Health Score** (0-100) with detailed breakdown
- 💡 **LLM-Generated Advice** using Phi-2 local model
- 🎯 **Savings Goals** with realistic timelines
- 💰 **Investment Suggestions** adjusted to your risk profile
- 📈 **Spending Analysis** with category breakdown
- ⚡ **Lightweight** - Runs in ~1.5GB RAM with LLM

### RAG System
- **LLM**: Phi-2 (2.7B) in Q4_K_M GGUF format
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (CPU-only)
- **Context Retrieval**: Top-k similarity search
- **Professional Prompts**: SEBI-compliant financial planner template

## 🚀 Quick Start

### Mode 1: LLM RAG Mode (Recommended)

**Full AI-powered advice with local Phi-2 model**

```cmd
# 1. Setup
setup_llm_mode.bat

# 2. Download model (~1.6GB)
python download_models.py

# 3. Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

# 4. Check RAG status
curl http://localhost:8010/rag/status
```

**RAM Usage**: ~1.5GB  
**Response Time**: 3-6 seconds  
**Documentation**: [LLM_RAG_GUIDE.md](LLM_RAG_GUIDE.md)

### Mode 2: Lightweight Mode (No LLM)

**Rule-based advice, minimal RAM**

```cmd
# 1. Setup
setup_lightweight.bat

# 2. Start server
start_server_lightweight.bat
```

**RAM Usage**: ~300MB  
**Response Time**: <1 second  
**Documentation**: [LIGHTWEIGHT_SETUP.md](LIGHTWEIGHT_SETUP.md)

## 📊 Example Output

```
💰 Financial Health: Good (75/100)

Monthly Income: ₹100,000
Monthly Expenses: ₹65,000
Net Surplus: ₹35,000 (35% savings rate)

✅ You're saving 35% of your income. Excellent work!

🔍 SPENDING INSIGHTS:
  • Your highest expense is rent: ₹24,000 (36.9%)
  • Grocery spending is well-controlled

🎯 SAVINGS RECOMMENDATIONS:
  • Emergency Fund Goal: ₹300,000 (3 months)
  • Build this in 8.6 months with current surplus

📊 INVESTMENT SUGGESTIONS (Medium Risk):
  • 50% Equity mutual funds
  • 30% Debt funds
  • 20% Gold/International funds

🎯 ACTION ITEMS:
  • This week: Set up automatic savings transfer
  • This month: Open high-yield savings account
  • Next month: Start SIP with ₹10,500
```

## 📝 CSV Format

Create a CSV file with your transactions:

```csv
date,amount,description
2025-11-01,50000,Salary November
2025-11-02,-2000,Groceries
2025-11-05,-12000,Rent
2025-11-07,-500,Netflix
```

**Rules:**
- Date: YYYY-MM-DD format
- Amount: Positive for income, negative for expenses
- Description: Any text (used for auto-categorization)

## 🔌 API Endpoints

### Upload Transactions
```bash
curl -X POST "http://localhost:8010/upload_csv?user_id=1" \
  -F "file=@your_transactions.csv"
```

### Get Insights
```bash
curl "http://localhost:8010/insights/1?risk_profile=medium"
```

Risk profiles: `low`, `medium`, `high`

### View API Docs
Open: http://localhost:8010/docs

## 💡 How It Works

### 1. RAG System
- **Knowledge Base**: 10+ financial best practices
- **Context Retrieval**: Finds relevant advice for your situation
- **Personalization**: Adapts to your income, expenses, and risk profile

### 2. Financial Health Score

| Score | Rating | Meaning |
|-------|--------|---------|
| 80-100 | Excellent | Strong financial position |
| 60-79 | Good | Healthy with room for improvement |
| 40-59 | Fair | Needs attention |
| 0-39 | Needs Improvement | Immediate action required |

**Score Factors:**
- Savings rate (20%+ is excellent)
- Spending diversity
- Transaction tracking
- Income regularity

### 3. Automatic Categorization

| Category | Keywords |
|----------|----------|
| Income | salary, payroll, wage |
| Groceries | grocery, supermarket |
| Rent | rent, apartment |
| Transport | uber, ola, taxi |
| Other | Everything else |

## 🛠️ System Requirements

### Lightweight Mode (Recommended)
- **RAM**: 4GB (uses ~300MB)
- **Disk**: 200MB
- **Docker**: Not required
- **Redis**: Not required

### Features Available
✅ Upload CSV  
✅ RAG insights  
✅ Financial health score  
✅ Savings recommendations  
✅ Investment suggestions  
✅ Action items  
❌ Background monitoring (requires Redis)  

## 📚 Documentation

- **README.md** (this file) - Main documentation
- **LIGHTWEIGHT_SETUP.md** - Detailed setup guide
- **QUICK_REFERENCE.md** - Command reference

## 🔧 Troubleshooting

### Python not found
Install Python 3.11+ from https://www.python.org/downloads/

### Cannot activate virtual environment
```powershell
# PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8010 already in use
```cmd
netstat -ano | findstr :8010
taskkill /PID <PID_NUMBER> /F
```

### Out of memory
Close other applications and use lightweight mode.

## 🧪 Testing

### Test Calculations
```bash
python test_calculations.py
```

### Test Full System
```bash
python test_rag_system.py
```

## 🎓 Tips for Best Results

1. **Upload complete data**: At least 1 month of transactions
2. **Include income**: System needs income for accurate analysis
3. **Consistent descriptions**: Use similar terms for recurring expenses
4. **Regular updates**: Upload monthly to track progress
5. **Try risk profiles**: See how advice changes

## 🛠️ Technology Stack

- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **NumPy**: Vector operations for RAG
- **Structlog**: Structured logging
- **SQLite**: Local database

## 📈 Performance

- **Startup**: 3-5 seconds
- **Response time**: 1-2 seconds
- **RAM usage**: ~300MB
- **Concurrent users**: 1-2

## 🔐 Security & Privacy

- All data stored locally in SQLite
- No external API calls
- No data leaves your machine
- Can run completely offline

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- LLM integration (OpenAI, Anthropic)
- Advanced embeddings (sentence-transformers)
- Goal tracking features
- Multi-currency support
- Predictive analytics

## 📄 License

MIT License - feel free to use and modify!

## 🚀 Next Steps

1. Run `setup_lightweight.bat`
2. Start server with `start_server_lightweight.bat`
3. Upload your transactions
4. Get personalized insights
5. Follow action items
6. Track progress monthly

---

**Start making smarter financial decisions today! 💰📈**

Questions? Check [LIGHTWEIGHT_SETUP.md](LIGHTWEIGHT_SETUP.md) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
