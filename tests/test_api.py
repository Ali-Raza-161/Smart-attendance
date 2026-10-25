import sys, os, io
os.environ["DATABASE_URL"] = "sqlite:////tmp/smart_attendance_test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from fastapi.testclient import TestClient

if os.path.exists("/tmp/smart_attendance_test.db"):
    os.remove("/tmp/smart_attendance_test.db")

from api.services.db import init_db, SessionLocal
from api.services.auth import hash_password
from api.models.models import User
from api.main import app

init_db()
db = SessionLocal()
db.add(User(name="Test Admin", email="admin@test.local",
            password_hash=hash_password("test1234"), role="admin"))
db.commit(); db.close()
client = TestClient(app)

def _token():
    r = client.post("/api/auth/login", json={"email": "admin@test.local", "password": "test1234"})
    assert r.status_code == 200, r.text
    return r.json()["token"]

def test_health():
    assert client.get("/health").json()["ok"] is True

def test_login_wrong_password_rejected():
    r = client.post("/api/auth/login", json={"email": "admin@test.local", "password": "wrong"})
    assert r.status_code == 401

def test_unauthenticated_people_rejected():
    assert client.get("/api/people").status_code == 401

def test_class_person_session_and_correction_flow():
    tok = _token(); h = {"Authorization": f"Bearer {tok}"}
    c = client.post("/api/classes", json={"name": "Class 5"}, headers=h); assert c.status_code == 200, c.text
    class_id = c.json()["id"]
    p = client.post("/api/people", json={"name": "Test Student", "roll_or_employee_no": "5-01",
                                         "class_id": class_id, "consent": True}, headers=h)
    assert p.status_code == 200, p.text
    person_id = p.json()["id"]
    s = client.post("/api/sessions", json={"class_id": class_id, "date": "2026-10-25"}, headers=h)
    assert s.status_code == 200, s.text
    att = client.get(f"/api/sessions/{s.json()['id']}/attendance", headers=h).json()
    assert len(att) == 1 and att[0]["status"] == "absent"  # manual fallback
    patch = client.patch(f"/api/attendance/{att[0]['id']}", json={"status": "present"}, headers=h)
    assert patch.status_code == 200 and patch.json()["status"] == "present"

def test_enroll_without_consent_rejected():
    tok = _token(); h = {"Authorization": f"Bearer {tok}"}
    p = client.post("/api/people", json={"name": "No Consent", "roll_or_employee_no": "NC-1",
                                         "consent": False}, headers=h)
    pid = p.json()["id"]
    r = client.post(f"/api/people/{pid}/enroll", files={"files": ("face.png", b"not-an-image", "image/png")}, headers=h)
    assert r.status_code == 400  # consent gate fires before any model work

def test_recognize_invalid_and_oversized_rejected():
    tok = _token(); h = {"Authorization": f"Bearer {tok}"}
    s = client.post("/api/sessions", json={"class_id": 1, "date": "2026-10-25"}, headers=h)
    sid = s.json()["id"]
    bad = client.post(f"/api/sessions/{sid}/recognize",
                      files={"file": ("x.txt", b"hello", "text/plain")}, headers=h)
    assert bad.status_code == 400
    big = client.post(f"/api/sessions/{sid}/recognize",
                      files={"file": ("big.png", b"x" * (6 * 1024 * 1024), "image/png")}, headers=h)
    assert big.status_code in (400, 413)

def test_delete_person_removes_face_data():
    tok = _token(); h = {"Authorization": f"Bearer {tok}"}
    p = client.post("/api/people", json={"name": "To Delete", "roll_or_employee_no": "DEL-1",
                                         "consent": True}, headers=h)
    pid = p.json()["id"]
    d = client.delete(f"/api/people/{pid}", headers=h)
    assert d.status_code == 200 and d.json()["face_data_deleted"] is True
    people = client.get("/api/people", headers=h).json()
    assert all(x["id"] != pid for x in people)

def test_report_export_is_xlsx():
    tok = _token(); h = {"Authorization": f"Bearer {tok}"}
    r = client.get("/api/reports/export", headers=h)
    assert r.status_code == 200
    assert r.content[:2] == b"PK"  # zip/xlsx header
