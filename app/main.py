# app/main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
import os, io, json
from .tools import parse_csv_bytes
from .agents import ingest_agent, analysis_agent, advisor_agent
from .db import init_db, SessionLocal
from .models import Transaction, User, Advice
from .schemas import AdvisorRequest
from .telemetry import init_tracing, init_structlog
from dotenv import load_dotenv
import asyncio
from structlog import get_logger

# Optional imports for features that can be disabled
CELERY_AVAILABLE = False
PROMETHEUS_AVAILABLE = False

try:
    from .tasks import monitor_user_finances
    CELERY_AVAILABLE = True
except ImportError:
    pass

try:
    from prometheus_client import start_http_server, Counter, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    pass

load_dotenv()
init_tracing()
init_structlog()

log = get_logger()

APP_PORT = int(os.getenv("APP_PORT", 8010))
METRICS_PORT = int(os.getenv("PROMETHEUS_METRICS_PORT", 8001))

app = FastAPI(title="AI Financial Advisor with Local LLM RAG")

# Initialize RAG system at startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG system"""
    log.info("app_startup", port=APP_PORT)
    
    # Initialize database
    init_db()
    log.info("database_initialized")
    
    # Initialize LLM RAG system
    try:
        from .llm_rag_engine import initialize_rag_system
        initialize_rag_system()
        log.info("llm_rag_system_initialized")
    except Exception as e:
        log.warning("llm_rag_initialization_failed", 
                   error=str(e),
                   message="System will use fallback rule-based advice")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    log.info("app_shutdown")

# init DB
init_db()

# prometheus metrics (optional)
if PROMETHEUS_AVAILABLE:
    AGENT_RUNS = Counter('agent_runs_total', 'Total agent runs', ['agent'])
    AGENT_DURATION = Histogram('agent_run_duration_seconds', 'Agent duration', ['agent'])
    
    def measure(agent_name: str):
        def decorator(fn):
            async def wrapper(*args, **kwargs):
                AGENT_RUNS.labels(agent=agent_name).inc()
                import time
                t0 = time.time()
                res = await fn(*args, **kwargs)
                AGENT_DURATION.labels(agent=agent_name).observe(time.time() - t0)
                return res
            return wrapper
        return decorator
    
    # start prometheus exporter port in background
    try:
        start_http_server(METRICS_PORT)
        log.info("prometheus_started", port=METRICS_PORT)
    except Exception as e:
        log.warning("prometheus_start_failed", error=str(e), port=METRICS_PORT)
else:
    # No-op decorator when Prometheus is not available
    def measure(agent_name: str):
        def decorator(fn):
            return fn
        return decorator
    log.info("prometheus_disabled", reason="prometheus-client not installed")


ingest = measure("ingest")(ingest_agent)
analysis = measure("analysis")(analysis_agent)
advisor = measure("advisor")(advisor_agent)

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), user_id: int = None):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        rows = parse_csv_bytes(content)
        if not rows:
            raise HTTPException(status_code=400, detail="No valid rows found in CSV")
        
        # ingest
        transactions = await ingest(rows)
        
        # persist transactions (optional user)
        db = SessionLocal()
        try:
            if user_id is None:
                # create temp user
                u = User(name="demo", email=None)
                db.add(u)
                db.commit()
                db.refresh(u)
                user_id = u.id
            else:
                # Verify user exists
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            for t in transactions:
                tx = Transaction(
                    user_id=user_id, 
                    date=t["date"], 
                    amount=t["amount"], 
                    description=t["description"], 
                    category=t["category"], 
                    raw=t["raw"]
                )
                db.add(tx)
            db.commit()
        finally:
            db.close()
        
        # analysis & advisor with RAG
        analysis_res = await analysis(transactions)
        advice_res = await advisor(analysis_res, {"risk_profile": "medium"}, transactions)
        log.info("pipeline_complete", user_id=user_id, transactions=len(transactions))
        
        return {
            "user_id": user_id, 
            "transactions_ingested": len(transactions), 
            "analysis": analysis_res, 
            "advice": advice_res
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("upload_csv_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/start_monitor/{user_id}")
def start_monitor(user_id: int, iterations: int = 10, pause_seconds: int = 60):
    """
    Start monitor long-running task (requires Celery)
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Background monitoring is not available. Celery/Redis not configured. Use /insights endpoint instead for on-demand analysis."
        )
    
    try:
        # Validate user exists
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        finally:
            db.close()
        
        # Validate parameters
        if iterations < 1 or iterations > 1000:
            raise HTTPException(status_code=400, detail="iterations must be between 1 and 1000")
        if pause_seconds < 1:
            raise HTTPException(status_code=400, detail="pause_seconds must be at least 1")
        
        # kick off a Celery background task
        task = monitor_user_finances.apply_async(
            args=(user_id, iterations, pause_seconds), 
            queue="monitor_queue"
        )
        log.info("monitor_started", user_id=user_id, task_id=task.id)
        return {"task_id": task.id, "user_id": user_id, "iterations": iterations}
    except HTTPException:
        raise
    except Exception as e:
        log.error("start_monitor_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to start monitor: {str(e)}")
async def upload_csv(file: UploadFile = File(...), user_id: int = None):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        rows = parse_csv_bytes(content)
        if not rows:
            raise HTTPException(status_code=400, detail="No valid rows found in CSV")
        
        # ingest
        transactions = await ingest(rows)
        
        # persist transactions (optional user)
        db = SessionLocal()
        try:
            if user_id is None:
                # create temp user
                u = User(name="demo", email=None)
                db.add(u)
                db.commit()
                db.refresh(u)
                user_id = u.id
            else:
                # Verify user exists
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            for t in transactions:
                tx = Transaction(
                    user_id=user_id, 
                    date=t["date"], 
                    amount=t["amount"], 
                    description=t["description"], 
                    category=t["category"], 
                    raw=t["raw"]
                )
                db.add(tx)
            db.commit()
        finally:
            db.close()
        
        # analysis & advisor with RAG
        analysis_res = await analysis(transactions)
        advice_res = await advisor(analysis_res, {"risk_profile": "medium"}, transactions)
        log.info("pipeline_complete", user_id=user_id, transactions=len(transactions))
        
        return {
            "user_id": user_id, 
            "transactions_ingested": len(transactions), 
            "analysis": analysis_res, 
            "advice": advice_res
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("upload_csv_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/start_monitor/{user_id}")
def start_monitor(user_id: int, iterations: int = 10, pause_seconds: int = 60):
    """
    Start monitor long-running task (demo uses limited iterations)
    """
    try:
        # Validate user exists
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        finally:
            db.close()
        
        # Validate parameters
        if iterations < 1 or iterations > 1000:
            raise HTTPException(status_code=400, detail="iterations must be between 1 and 1000")
        if pause_seconds < 1:
            raise HTTPException(status_code=400, detail="pause_seconds must be at least 1")
        
        # kick off a Celery background task
        task = monitor_user_finances.apply_async(
            args=(user_id, iterations, pause_seconds), 
            queue="monitor_queue"
        )
        log.info("monitor_started", user_id=user_id, task_id=task.id)
        return {"task_id": task.id, "user_id": user_id, "iterations": iterations}
    except HTTPException:
        raise
    except Exception as e:
        log.error("start_monitor_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to start monitor: {str(e)}")

@app.get("/advices/{user_id}")
def get_advices(user_id: int):
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        advs = db.query(Advice).filter(Advice.user_id == user_id).order_by(Advice.created_at.desc()).all()
        return {
            "count": len(advs), 
            "user_id": user_id,
            "advices": [
                {
                    "id": a.id, 
                    "advice": a.advice_blob, 
                    "created_at": a.created_at.isoformat()
                } for a in advs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("get_advices_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve advices: {str(e)}")
    finally:
        db.close()

@app.get("/insights/{user_id}")
async def get_financial_insights(user_id: int, risk_profile: str = "medium"):
    """
    Get comprehensive RAG-powered financial insights for a user
    """
    from .rag_engine import get_rag_engine
    
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get all transactions
        txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        if not txs:
            raise HTTPException(status_code=404, detail=f"No transactions found for user {user_id}")
        
        # Convert to dict format
        transactions = [
            {
                "date": t.date,
                "amount": t.amount,
                "description": t.description,
                "category": t.category
            }
            for t in txs
        ]
        
        # Run analysis
        analysis_res = await analysis(transactions)
        
        # Get RAG-powered advice
        rag = get_rag_engine()
        insights = rag.generate_personalized_advice(
            transactions,
            analysis_res,
            {"risk_profile": risk_profile}
        )
        
        log.info("insights_generated", user_id=user_id, health_score=insights["financial_health"]["score"])
        
        return {
            "user_id": user_id,
            "transaction_count": len(transactions),
            "analysis": analysis_res,
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("get_insights_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")
    finally:
        db.close()

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-financial-advisor"}

@app.get("/rag/status")
def rag_status():
    """Get RAG system status"""
    try:
        from .llm_rag_engine import get_system_status
        status = get_system_status()
        return {
            "status": "operational" if status['initialized'] else "not_initialized",
            "details": status
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
