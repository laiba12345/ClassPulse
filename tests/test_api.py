from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_lesson_catalog():
    assert client.get("/api/health").json()["status"] == "ok"
    lessons = client.get("/api/classes").json()
    assert len(lessons) == 3

def test_sse_stream_has_ordered_live_messages():
    with client.stream("GET", "/api/stream/fractions-live?speed=10000") as response:
        text = "".join(response.iter_text())
    assert response.status_code == 200
    assert "event: event" in text
    assert "event: ccs" in text
    assert "event: nudge" in text

def test_dashboard_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "ClassPulse" in response.text

def test_real_dataset_evidence_endpoint():
    response = client.get("/api/evidence/real-data")
    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset"] == "TalkMoves"
    assert payload["total_rows"] > 2000

def test_live_input_enters_same_sse_stream_with_visible_tag():
    submitted = client.post("/api/live-input/forces-live", json={"student_id": "Live Guest", "text": "I am confused about the force", "timestamp": "2026-07-19T10:00:00Z"})
    assert submitted.status_code == 202
    with client.stream("GET", "/api/stream/forces-live?speed=10000") as response:
        text = "".join(response.iter_text())
    assert '"live": true' in text
    assert "Live Guest" in text
