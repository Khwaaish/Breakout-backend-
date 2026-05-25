# Closira Backend API

## Project overview
Closira Backend API handles customer enquiries, matches them to SOPs, schedules followups, and records timeline events. It uses FastAPI, SQLAlchemy, and Pydantic with background processing for SOP matching.

## Architecture
- FastAPI application exposing REST endpoints
- SQLAlchemy ORM models for persistence
- BackgroundTasks to process enquiries asynchronously
- Structured logging for important events
- CRUD layer isolates DB access from routes

## Folder structure
- `main.py` - FastAPI app entrypoint
- `app/` - application package
  - `models.py` - SQLAlchemy models
  - `crud.py` - DB access functions
  - `database.py` - DB config and session
  - `routes/` - API route modules
  - `services/` - business services (SOP matcher)
  - `workers/` - background worker functions
  - `schemas.py` - Pydantic request/response schemas
- `tests/` - pytest test suite

## Tech stack
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- BackgroundTasks
- pytest

## Project flow
1. `POST /enquiry` — enquiry created, status `queued`
2. Background worker runs (via `BackgroundTasks`) and attempts SOP match
3. Result: `processed` with `matched_sop` OR `escalated`

## API endpoints
- `POST /enquiry` — create enquiry
- `POST /enquiry/{job_id}/followup` — schedule followup
- `GET /enquiry/{job_id}/history` — get enquiry history and timeline
- `GET /health` — health check

## Setup
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix
source venv/bin/activate
pip install -r requirements.txt
```
Run server:
```bash
uvicorn main:app --reload
```
Run tests:
```bash
pytest -q
```

## Example curl requests
Create enquiry:
```bash
curl -X POST http://localhost:8000/enquiry -H "Content-Type: application/json" -d '{"customer_name":"John","channel":"email","message":"Need pricing information"}'
```
Create followup:
```bash
curl -X POST http://localhost:8000/enquiry/<job_id>/followup -H "Content-Type: application/json" -d '{"delay_minutes":30,"template_message":"Reminder"}'
```
Get history:
```bash
curl http://localhost:8000/enquiry/<job_id>/history
```
Health:
```bash
curl http://localhost:8000/health
```

## Architecture principles
- CRUD isolation: all DB access through `app/crud.py`
- Background processing: keep API responsive by offloading SOP matching
- Structured logging: JSON-like logs with event names
- Validation layer: Pydantic enforces input contracts

*** End of README ***
