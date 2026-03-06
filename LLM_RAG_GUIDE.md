# Local LLM RAG System Guide

Production-ready financial advisory system with Phi-2 LLM, optimized for 4GB RAM, CPU-only.

## System Architecture

```
CSV Upload
    ↓
Ingest Agent (categorization)
    ↓
Analysis Agent (metrics calculation)
    ↓
Build Financial Summary
    ↓
Embed with sentence-transformers (all-MiniLM-L6-v2)
    ↓
Store in FAISS Vector Database
    ↓
Retrieve Relevant Context (k=2)
    ↓
Generate Prompt with Context
    ↓
Phi-2 LLM (2.7B, Q4_K_M GGUF)
    ↓
Parse & Structure Response
    ↓
Return JSON Advice
```

## Technical Specifications

### LLM Configuration
- **Model**: Phi-2 (2.7B parameters)
- **Quantization**: Q4_K_M GGUF (4-bit)
- **Size**: ~1.6GB on disk, ~800MB in RAM
- **Context Window**: 1024 tokens
- **Max Generation**: 300 tokens
- **Threads**: 2 (CPU-only)
- **GPU Layers**: 0 (CPU-only)

### Embeddings
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimension**: 384
- **Size**: ~90MB
- **Speed**: ~1000 sentences/sec on CPU

### Vector Store
- **Engine**: FAISS (CPU)
- **Index Type**: IndexFlatL2
- **Storage**: In-memory
- **Retrieval**: Top-k similarity search

### Total RAM Usage
- Phi-2 Model: ~800MB
- Embeddings: ~100MB
- FAISS Index: ~50MB
- FastAPI: ~200MB
- **Total**: ~1.5GB (leaves 2.5GB free on 4GB system)

## Setup Instructions

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install LLM RAG dependencies
pip install -r requirements-llm.txt
```

### Step 2: Download Phi-2 Model

**Option A: Automated Download**
```bash
python download_models.py
```

**Option B: Manual Download**
1. Go to: https://huggingface.co/TheBloke/phi-2-GGUF
2. Download: `phi-2.Q4_K_M.gguf` (~1.6GB)
3. Place in: `models/phi-2.Q4_K_M.gguf`

### Step 3: Start Server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Wait for initialization messages:
```
INFO: database_initialized
INFO: llm_rag_system_initialized
INFO: Application startup complete
```

### Step 4: Verify RAG System

```bash
curl http://localhost:8010/rag/status
```

Expected response:
```json
{
  "status": "operational",
  "details": {
    "initialized": true,
    "embedding_model_loaded": true,
    "llm_model_loaded": true,
    "faiss_index_size": 0,
    "documents_stored": 0
  }
}
```

## Usage

### Upload CSV and Get LLM-Generated Advice

```bash
curl -X POST "http://localhost:8010/upload_csv?user_id=1" \
  -F "file=@Sample data/enhanced_transactions.csv"
```

Response includes LLM-generated advice:
```json
{
  "user_id": 1,
  "transactions_ingested": 32,
  "analysis": {
    "income": 100000,
    "expense": 65000,
    "surplus": 35000
  },
  "advice": {
    "summary": "Your financial health is good with a 35% savings rate...",
    "risk_assessment": "Spending is well-controlled. No major red flags...",
    "budget_recommendation": "Apply 50-30-20 rule: ₹50,000 for needs...",
    "investment_suggestion": "Moderate risk profile: 50% equity mutual funds...",
    "emergency_fund_strategy": "Target ₹390,000 (6 months). Achievable in 11 months...",
    "action_steps": [
      "Set up automatic transfer of ₹7,000 to savings",
      "Open high-yield savings account",
      "Start SIP with ₹10,500 in index fund"
    ]
  }
}
```

### Get Detailed Insights

```bash
curl "http://localhost:8010/insights/1?risk_profile=medium"
```

## Prompt Engineering

The system uses a SEBI-compliant financial planner prompt:

```
You are a SEBI-compliant certified financial planner for Indian middle-class clients.
Analyze the following structured financial data carefully.

FINANCIAL PROFILE:
- Monthly Income: ₹100,000
- Monthly Expenses: ₹65,000
- Net Surplus: ₹35,000
- Savings Rate: 35.0%
- Risk Profile: MEDIUM

EXPENSE BREAKDOWN:
- Groceries: ₹8,600 (13.2%)
- Rent: ₹24,000 (36.9%)
- Transport: ₹3,050 (4.7%)
- Other: ₹29,350 (45.2%)

Your responsibilities:
1. Interpret monthly income and expenses
2. Identify overspending categories
3. Calculate and evaluate savings rate
4. Assess financial health
5. Suggest optimized budget allocation using 50-30-20 rule
6. Recommend emergency fund target (in months of expenses)
7. Suggest investment allocation based on risk profile
8. Provide clear actionable next steps

Rules:
- Use numbers explicitly from the data above
- Be precise and realistic
- Avoid generic textbook advice
- Keep response under 300 words
- Maintain professional tone
- Focus on Indian financial context (PPF, EPF, NPS, mutual funds, etc.)
```

## Performance Optimization

### Memory Management

The system automatically handles memory constraints:

```python
# Normal config
n_ctx = 1024
max_tokens = 300

# Fallback config (if memory pressure)
n_ctx = 512
max_tokens = 150
```

### Response Time

- **Embedding**: ~50ms
- **FAISS Retrieval**: ~10ms
- **LLM Generation**: 2-5 seconds (CPU-only)
- **Total**: ~3-6 seconds per request

### Concurrent Requests

- **Recommended**: 1-2 concurrent users
- **Maximum**: 3 users (with queuing)

## Fallback Behavior

If LLM is unavailable (model not downloaded or initialization failed):

1. System logs warning
2. Falls back to rule-based advice
3. Still provides structured JSON response
4. No system crash

Example fallback response:
```json
{
  "summary": "Monthly surplus: ₹35,000. Savings rate: 35.0%.",
  "risk_assessment": "Financial position is stable.",
  "budget_recommendation": "Apply 50-30-20 rule...",
  "investment_suggestion": "Moderate: 50% equity, 30% debt, 20% gold",
  "emergency_fund_strategy": "Target: ₹390,000 (6 months)...",
  "action_steps": [...]
}
```

## Troubleshooting

### Model Not Loading

**Error**: `phi2_model_not_found`

**Solution**:
```bash
python download_models.py
```

### Out of Memory

**Error**: System crashes or becomes unresponsive

**Solutions**:
1. Close other applications
2. Reduce context window in `app/llm_rag_engine.py`:
   ```python
   LLM_CONFIG = {
       "n_ctx": 512,  # Reduced from 1024
       "max_tokens": 150,  # Reduced from 300
   }
   ```
3. Use rule-based fallback mode

### Slow Response

**Issue**: LLM takes >10 seconds

**Solutions**:
1. Increase CPU threads (if you have 4+ cores):
   ```python
   "n_threads": 4,  # Increased from 2
   ```
2. Reduce max_tokens:
   ```python
   "max_tokens": 200,  # Reduced from 300
   ```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'llama_cpp'`

**Solution**:
```bash
pip install -r requirements-llm.txt
```

## Production Deployment

### System Requirements

**Minimum**:
- RAM: 4GB
- CPU: Dual-core 2.0GHz
- Disk: 3GB free
- OS: Windows 10+, Ubuntu 20.04+, macOS 11+

**Recommended**:
- RAM: 6GB
- CPU: Quad-core 2.5GHz
- Disk: 5GB free
- SSD storage

### Security Considerations

1. **Data Privacy**: All processing is local, no external API calls
2. **Model Safety**: Phi-2 is a general-purpose model, responses should be reviewed
3. **Input Validation**: CSV files are validated before processing
4. **Rate Limiting**: Implement rate limiting for production

### Monitoring

Check RAG system health:
```bash
curl http://localhost:8010/rag/status
```

Monitor logs for:
- `rag_system_initialized` - System ready
- `advice_generated` - Successful generation
- `llm_not_available` - Fallback mode active

## Comparison: LLM vs Rule-Based

| Feature | LLM Mode | Rule-Based |
|---------|----------|------------|
| Advice Quality | Contextual, nuanced | Generic, formulaic |
| Response Time | 3-6 seconds | <1 second |
| RAM Usage | ~1.5GB | ~300MB |
| Setup Complexity | High (model download) | Low |
| Offline Capability | Yes | Yes |
| Customization | Prompt engineering | Code changes |

## Advanced Configuration

### Custom Prompts

Edit `app/llm_rag_engine.py`, function `_build_financial_prompt()`:

```python
prompt = f"""Your custom prompt here...
{data_section}
Your custom instructions...
"""
```

### Adjust Generation Parameters

```python
LLM_CONFIG = {
    "temperature": 0.7,      # Lower = more focused (0.1-1.0)
    "top_p": 0.9,           # Nucleus sampling (0.1-1.0)
    "repeat_penalty": 1.1,  # Avoid repetition (1.0-1.5)
}
```

### Vector Store Persistence

To save FAISS index to disk:

```python
import faiss

# Save
faiss.write_index(_faiss_index, "faiss_index.bin")

# Load
_faiss_index = faiss.read_index("faiss_index.bin")
```

## FAQ

**Q: Can I use a different LLM?**  
A: Yes, modify `_load_llm_model()` to load any GGUF model. Keep it ≤3B parameters for 4GB RAM.

**Q: Does it work offline?**  
A: Yes, completely offline after initial setup and model download.

**Q: Can I use GPU?**  
A: Yes, set `n_gpu_layers > 0` in LLM_CONFIG. Requires CUDA-enabled llama-cpp-python.

**Q: How accurate is the advice?**  
A: Phi-2 provides reasonable financial advice but should not replace professional financial advisors. Always review recommendations.

**Q: Can I fine-tune the model?**  
A: GGUF models cannot be fine-tuned. Use prompt engineering or switch to a trainable model format.

---

**Production-ready local LLM RAG system for financial advisory! 🚀💰**

For support, check logs and RAG status endpoint.
