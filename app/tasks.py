# app/tasks.py
from celery import Celery
import os
import time
from .db import SessionLocal
from .models import Transaction, Advice, User
from .agents import analysis_agent, advisor_agent
from structlog import get_logger
import asyncio

log = get_logger()

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

celery = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery.task(name="monitor_user_finances", bind=True)
def monitor_user_finances(self, user_id: int, iterations: int = 10, pause_seconds: int = 60):
    """
    Long-running monitor agent: re-evaluates periodically. Demonstrates loop agent with pause/resume.
    iterations: number of loops (for demo); set large for production or schedule periodically instead.
    """
    db = SessionLocal()
    try:
        for i in range(iterations):
            log.info("monitor_iteration_start", user_id=user_id, iteration=i+1)
            # load user's recent transactions
            txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
            # convert ORM rows to dicts
            rows = [{"date": t.date, "amount": t.amount, "description": t.description, "category": t.category} for t in txs]
            # run analysis and advisor synchronously on event loop
            loop = asyncio.get_event_loop()
            analysis = loop.run_until_complete(analysis_agent(rows))
            advice = loop.run_until_complete(advisor_agent(analysis, {"risk_profile": "medium"}))
            # save advice to DB
            new = Advice(user_id=user_id, advice_blob=advice)
            db.add(new)
            db.commit()
            log.info("monitor_iteration_finished", user_id=user_id, iteration=i+1)
            # simple pause/resume: check if task requested to revoke
            time.sleep(pause_seconds)
    except Exception as e:
        log.error("monitor_error", error=str(e))
        raise
    finally:
        db.close()
