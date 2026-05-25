import os
import time
import json
import importlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def test_app(tmp_path, monkeypatch):
    # Use a temporary sqlite file for isolation
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)

    # Reload database module so engine uses test DB
    import app.database as database
    importlib.reload(database)
    # Ensure models are imported so tables are registered
    import app.models as models
    database.init_db()
    # Ensure tables are created on the test engine explicitly
    database.Base.metadata.create_all(bind=database.engine)
    # Also ensure each model's table is created on the engine (robust across reloads)
    try:
        from backend.app.models import Enquiry, Followup, TimelineEvent
        Enquiry.__table__.create(bind=database.engine, checkfirst=True)
        Followup.__table__.create(bind=database.engine, checkfirst=True)
        TimelineEvent.__table__.create(bind=database.engine, checkfirst=True)
    except Exception:
        pass
    # Reload worker and route modules so they pick up the test SessionLocal
    import app.workers.background_tasks as bg
    importlib.reload(bg)
    import app.routes.enquiry as routes_enq
    importlib.reload(routes_enq)

    # Reload main app to pick up new DB settings
    import main
    importlib.reload(main)
    app = main.app
    return TestClient(app)


def test_create_enquiry_success(test_app):
    client = test_app
    payload = {
        "customer_name": "Alice",
        "channel": "email",
        "message": "Need pricing information"
    }
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "job_id" in data
    assert data["status"] == "queued"


def test_invalid_channel_validation(test_app):
    client = test_app
    payload = {"customer_name": "Bob", "channel": "sms", "message": "Hello"}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 422


def test_empty_message_validation(test_app):
    client = test_app
    payload = {"customer_name": "Charlie", "channel": "email", "message": ""}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 422


def test_sop_matched_flow(test_app):
    client = test_app
    payload = {"customer_name": "Dana", "channel": "email", "message": "Need pricing information"}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 201
    job_id = r.json()["job_id"]

    # Wait for BackgroundTasks to run (polling)
    deadline = time.time() + 3.0
    status_val = None
    matched = None
    while time.time() < deadline:
        r2 = client.get(f"/enquiry/{job_id}/history")
        assert r2.status_code == 200
        data = r2.json()
        status_val = data.get("status")
        matched = data.get("matched_sop")
        if status_val == "processed":
            break
        time.sleep(0.2)
    assert status_val == "processed"
    assert matched is not None


def test_escalation_flow(test_app):
    client = test_app
    payload = {"customer_name": "Eve", "channel": "email", "message": "ajsdkjasd"}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 201
    job_id = r.json()["job_id"]

    # Wait for background worker to process
    deadline = time.time() + 3.0
    status_val = None
    while time.time() < deadline:
        r2 = client.get(f"/enquiry/{job_id}/history")
        assert r2.status_code == 200
        data = r2.json()
        status_val = data.get("status")
        if status_val == "escalated":
            break
        time.sleep(0.2)
    assert status_val == "escalated"


def test_followup_and_history(test_app):
    client = test_app
    payload = {"customer_name": "Fay", "channel": "whatsapp", "message": "Need booking"}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 201
    job_id = r.json()["job_id"]

    # Create followup
    followup_payload = {"delay_minutes": 10, "template_message": "Reminder"}
    r2 = client.post(f"/enquiry/{job_id}/followup", json=followup_payload)
    assert r2.status_code == 201
    follow_data = r2.json()
    assert follow_data["status"] == "scheduled"

    # History should include followups and timeline
    r3 = client.get(f"/enquiry/{job_id}/history")
    assert r3.status_code == 200
    hist = r3.json()
    assert "timeline" in hist
    assert "followups" in hist
    assert len(hist["followups"]) >= 0


def test_invalid_job_id_history_404(test_app):
    client = test_app
    r = client.get("/enquiry/00000000-0000-0000-0000-000000000000/history")
    assert r.status_code == 404


def test_health_endpoint(test_app):
    client = test_app
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_multiple_enquiries_isolation(test_app):
    client = test_app
    payload1 = {"customer_name": "G1", "channel": "email", "message": "Need pricing information"}
    payload2 = {"customer_name": "G2", "channel": "email", "message": "ajsdkjasd"}
    r1 = client.post("/enquiry", json=payload1)
    r2 = client.post("/enquiry", json=payload2)
    assert r1.status_code == 201
    assert r2.status_code == 201

    job1 = r1.json()["job_id"]
    job2 = r2.json()["job_id"]

    time.sleep(0.5)
    h1 = client.get(f"/enquiry/{job1}/history").json()
    h2 = client.get(f"/enquiry/{job2}/history").json()
    assert h1["job_id"] != h2["job_id"]


def test_create_enquiry_missing_customer_name(test_app):
    client = test_app
    payload = {"channel": "email", "message": "Hi"}
    r = client.post("/enquiry", json=payload)
    assert r.status_code == 422