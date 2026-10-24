import os
from pathlib import Path
from tempfile import TemporaryDirectory

_tmp = TemporaryDirectory()
os.environ["KISIV_DB_PATH"] = str(Path(_tmp.name) / "test.db")

from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"


def test_event_assess_and_dry_run_response():
    with TestClient(app) as client:
        r = client.post("/api/v1/events", json={
            "source": "pytest",
            "event_type": "repeated_login_failure",
            "severity": "high",
            "description": "多次登录失败，疑似暴力破解",
            "asset": "test-host",
            "metadata": {"test": True},
        })
        assert r.status_code == 201
        event_id = r.json()["id"]

        assessment = client.post(f"/api/v1/events/{event_id}/assess")
        assert assessment.status_code == 200
        assert assessment.json()["risk_level"] in {"high", "critical"}
        assert assessment.json()["score"] > 0

        response = client.post("/api/v1/responses", json={
            "event_id": event_id, "action": "block_source", "reason": "test only"
        })
        assert response.status_code == 200
        assert response.json()["dry_run"] is True
        assert response.json()["status"] == "simulated"


def test_unknown_event_returns_404():
    with TestClient(app) as client:
        r = client.post("/api/v1/responses", json={
            "event_id": "missing-event", "action": "alert"
        })
        assert r.status_code == 404


def test_event_input_validation_and_size_limits():
    with TestClient(app) as client:
        too_long = client.post("/api/v1/events", json={
            "source": "pytest",
            "event_type": "validation",
            "severity": "info",
            "description": "x" * 4001,
        })
        assert too_long.status_code == 422

        invalid_severity = client.post("/api/v1/events", json={
            "source": "pytest",
            "event_type": "validation",
            "severity": "unknown",
            "description": "safe test",
        })
        assert invalid_severity.status_code == 422


def test_audit_contains_event_and_assessment():
    with TestClient(app) as client:
        created = client.post("/api/v1/events", json={
            "source": "pytest",
            "event_type": "benign_test",
            "severity": "low",
            "description": "synthetic event for audit test",
        })
        assert created.status_code == 201
        event_id = created.json()["id"]

        assessed = client.post(f"/api/v1/events/{event_id}/assess")
        assert assessed.status_code == 200

        audit = client.get("/api/v1/audit?limit=20")
        assert audit.status_code == 200
        actions = [
            item["action"] for item in audit.json()["items"]
            if item["event_id"] == event_id
        ]
        assert "event.created" in actions
        assert "event.assessed" in actions
