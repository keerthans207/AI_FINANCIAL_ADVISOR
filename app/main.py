# app/main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
import os, io, json
from .tools import parse_csv_bytes
from .agents import ingest_agent, analysis_agent, advisor_agent
from .db import init_db, SessionLocal
from .models import Transaction, User, Advice
from .schemas import AdvisorRequest
from .telemetry import init_tracing, init_structlog
from prometheus_client import start_http_server, Counter, Histogram
from dotenv import load_dotenv
import asyncio
from structlog import get_logger
from .tasks import monitor_user_finances

load_dotenv()
init_tracing()
init_structlog()

log = get_logger()

APP_PORT = int(os.getenv("APP_PORT", 8000))
METRICS_PORT = int(os.getenv("PROMETHEUS_METRICS_PORT", 8001))

app = FastAPI(title="AI Financial Advisor")

# init DB
init_db()

# prometheus metrics
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

ingest = measure("ingest")(ingest_agent)
analysis = measure("analysis")(analysis_agent)
advisor = measure("advisor")(advisor_agent)

# start prometheus exporter port in background
start_http_server(METRICS_PORT)

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), user_id: int = None):
    content = await file.read()
    rows = parse_csv_bytes(content)
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
        for t in transactions:
            tx = Transaction(user_id=user_id, date=t["date"], amount=t["amount"], description=t["description"], category=t["category"], raw=t["raw"])
            db.add(tx)
        db.commit()
    finally:
        db.close()
    # analysis & advisor
    analysis_res = await analysis(transactions)
    advice_res = await advisor(analysis_res, {"risk_profile": "medium"})
    log.info("pipeline_complete", user_id=user_id)
    return {"user_id": user_id, "transactions_ingested": len(transactions), "analysis": analysis_res, "advice": advice_res}

@app.post("/start_monitor/{user_id}")
def start_monitor(user_id: int, iterations: int = 10, pause_seconds: int = 60):
    """
    Start monitor long-running task (demo uses limited iterations)
    """
    # kick off a Celery background task
    task = monitor_user_finances.apply_async(args=(user_id, iterations, pause_seconds), queue="monitor_queue")
    return {"task_id": task.id}

@app.get("/advices/{user_id}")
def get_advices(user_id: int):
    db = SessionLocal()
    try:
        advs = db.query(Advice).filter(Advice.user_id == user_id).order_by(Advice.created_at.desc()).all()
        return {"count": len(advs), "advices": [ {"id": a.id, "advice": a.advice_blob, "created_at": a.created_at.isoformat()} for a in advs ]}
    finally:
        db.close()
