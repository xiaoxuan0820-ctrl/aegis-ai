import os
from pathlib import Path
from tempfile import TemporaryDirectory
_tmp = TemporaryDirectory()
os.environ["AEGIS_DB_PATH"] = str(Path(_tmp.name) / "test.db")
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_health():
    r=client.get("/health"); assert r.status_code==200 and r.json()["status"]=="ok"
def test_event_assess_and_dry_run_response():
    r=client.post("/api/v1/events",json={"source":"pytest","event_type":"repeated_login_failure","severity":"high","description":"多次登录失败，疑似暴力破解","asset":"test-host","metadata":{"test":True}})
    assert r.status_code==201; event_id=r.json()["id"]
    assessment=client.post(f"/api/v1/events/{event_id}/assess")
    assert assessment.status_code==200 and assessment.json()["risk_level"] in {"high","critical"} and assessment.json()["score"]>0
    response=client.post("/api/v1/responses",json={"event_id":event_id,"action":"block_source","reason":"test only"})
    assert response.status_code==200 and response.json()["dry_run"] is True and response.json()["status"]=="simulated"
def test_unknown_event_returns_404():
    r=client.post("/api/v1/responses",json={"event_id":"missing-event","action":"alert"}); assert r.status_code==404
