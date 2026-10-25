import os, sys
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from api.services.db import get_db
from api.services.auth import require_role
from api.services.audit import log
from api.models.models import Session as AttSession, Person, Attendance
from api.schemas.schemas import SessionIn, AttendancePatch

router = APIRouter()
MAX_IMAGE_BYTES = 5 * 1024 * 1024

@router.post("/sessions")
def create_session(data: SessionIn, db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    s = AttSession(class_id=data.class_id, date=data.date, start_time=data.start_time, created_by=user.id)
    db.add(s); db.commit(); db.refresh(s)
    # Manual fallback: everyone in the class starts as absent; the teacher
    # reviews and corrects before saving. This keeps attendance working
    # for people who do not consent to face recognition.
    for p in db.query(Person).filter(Person.class_id == data.class_id).all():
        db.add(Attendance(session_id=s.id, person_id=p.id, status="absent", marked_by="teacher"))
    db.commit()
    log(db, "session_created", user.id, f"session:{s.id}")
    return {"id": s.id, "class_id": s.class_id, "date": s.date, "start_time": s.start_time}

@router.get("/sessions/{session_id}/attendance")
def session_attendance(session_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    rows = db.query(Attendance).filter(Attendance.session_id == session_id).all()
    out = []
    for r in rows:
        p = db.query(Person).filter(Person.id == r.person_id).first()
        out.append({"id": r.id, "session_id": r.session_id, "person_id": r.person_id,
                    "name": p.name if p else None, "status": r.status,
                    "confidence": r.confidence, "marked_by": r.marked_by})
    return out

@router.post("/sessions/{session_id}/recognize")
async def recognize(session_id: int, file: UploadFile = File(...),
                    db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    """Recognize faces in a frame/photo. Without a detector/embedding
    model this returns 503 — never a fake match. With a model, faces are
    returned for teacher review; nothing is saved as present until the
    teacher reviews and saves (see PATCH /attendance/{id})."""
    s = db.query(AttSession).filter(AttSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPG or PNG images are allowed.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image file.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 5 MB).")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from ai.detector import detect_faces, DetectorUnavailable
        boxes = detect_faces(data)
    except DetectorUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"Face detection model not available: {exc}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Could not decode image.")
    # Liveness + matching require an embedding model; without it, report
    # detected boxes only, with no identity claims.
    return {"session_id": session_id, "faces_detected": len(boxes),
            "faces": [b.to_dict() for b in boxes],
            "note": "Detection only. Identity matching requires an embedding model; teacher review is required before saving attendance."}

@router.patch("/attendance/{attendance_id}")
def correct_attendance(attendance_id: int, data: AttendancePatch,
                       db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    if data.status not in ("present", "absent", "late"):
        raise HTTPException(status_code=400, detail="Status must be present, absent or late.")
    r = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    r.status = data.status; r.marked_by = "teacher"; db.commit()
    log(db, "attendance_corrected", user.id, f"attendance:{attendance_id}:{data.status}")
    return {"id": r.id, "status": r.status, "marked_by": r.marked_by}
