AI Financial Advisor - Run instructions (Docker Compose)

Prereqs:
- Docker & docker-compose installed
- (optional) Python 3.11+ if you prefer local pip run

1) Clone repository
   git clone <repo-url> ai-financial-advisor
   cd ai-financial-advisor

2) Copy .env.sample -> .env and edit if needed
   cp .env.sample .env

3) Create data directory (for SQLite DB)
   mkdir -p data

4) Build & start services using docker-compose
   docker-compose up --build

   This will start:
   - Redis (on host:6379)
   - backend FastAPI on host:8000
   - Prometheus metrics exporter on host:8001
   - Celery worker (background tasks)
   - Flower UI on host:5555 (optional)

5) Test ingest pipeline (use curl or Postman):
   curl -X POST "http://localhost:8000/upload_csv?user_id=1" -F "file=@sample_data/sample_transactions.csv"

   Response: JSON with user_id, analysis and advice.

6) Start monitor (long-running loop agent):
   curl -X POST "http://localhost:8000/start_monitor/1" -d ""
   This triggers a Celery task that loops (default demo iterations=10).

7) Get advices:
   curl "http://localhost:8000/advices/1"

8) Metrics:
   Open http://localhost:8001/ to see Prometheus metrics (plain text).
   Optionally add Prometheus to scrape that endpoint.

9) Flower (Celery UI):
   Open http://localhost:5555

Notes for development without Docker:
- Create virtualenv, pip install -r requirements.txt
- Start Redis locally or change REDIS_URL to a running Redis instance.
- Run backend: uvicorn app.main:app --reload --port 8000
- Run celery worker: celery -A app.celery_worker.celery worker --loglevel=info -Q monitor_queue
