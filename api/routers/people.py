import json, os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from api.services.db import get_db
from api.services.auth import require_role
from api.services.audit import log
from api.models.models import Person, FaceEmbedding, Attendance, Class
from api.schemas.schemas import PersonIn, ClassIn

router = APIRouter()
MAX_IMAGE_BYTES = 5 * 1024 * 1024

def _person_out(p):
    return {"id": p.id, "name": p.name, "roll_or_employee_no": p.roll_or_employee_no,
            "class_id": p.class_id, "status": p.status, "consent": p.consent,
            "embedding_count": len(p.embeddings)}

@router.get("/classes")
def list_classes(db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    return [{"id": c.id, "name": c.name, "teacher_id": c.teacher_id} for c in db.query(Class).all()]

@router.post("/classes")
def create_class(data: ClassIn, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    c = Class(name=data.name, teacher_id=data.teacher_id)
    db.add(c); db.commit(); db.refresh(c)
    log(db, "class_created", user.id, f"class:{c.id}")
    return {"id": c.id, "name": c.name, "teacher_id": c.teacher_id}

@router.get("/people")
def list_people(db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    return [_person_out(p) for p in db.query(Person).all()]

@router.post("/people")
def create_person(data: PersonIn, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    p = Person(name=data.name, roll_or_employee_no=data.roll_or_employee_no,
               class_id=data.class_id, status=data.status, consent=data.consent)
    db.add(p); db.commit(); db.refresh(p)
    log(db, "person_created", user.id, f"person:{p.id}")
    return _person_out(p)

@router.post("/people/{person_id}/enroll")
async def enroll(person_id: int, files: list[UploadFile] = File(...),
                 db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    """Enrollment: validate images, then extract embeddings IF a model is
    available. Raw photos are NOT stored. Without a model this returns
    503 — it never invents a fake embedding. Written consent is required:
    the person record must have consent=True."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not person.consent:
        raise HTTPException(status_code=400, detail="Written consent is required before enrollment. Set consent=True on the person record first.")
    if not files or len(files) > 10:
        raise HTTPException(status_code=400, detail="Upload 1 to 10 face images.")
    contents = []
    for f in files:
        if f.content_type not in ("image/jpeg", "image/png", "image/jpg"):
            raise HTTPException(status_code=400, detail="Only JPG or PNG images are allowed.")
        data = await f.read()
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Image too large (max 5 MB).")
        if not data:
            raise HTTPException(status_code=400, detail="Empty image file.")
        contents.append(data)
    # Model-gated: do not store photos, do not fake embeddings.
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from ai.embedder import get_embedding, ModelNotAvailable
        from ai.detector import detect_faces, DetectorUnavailable
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Face model unavailable: {exc}")
    try:
        boxes = detect_faces(contents[0])
        if not boxes:
            return {"person_id": person_id, "enrolled": 0, "note": "No face detected in the first image; nothing was stored."}
        emb = get_embedding(contents[0])
    except (ModelNotAvailable, DetectorUnavailable) as exc:
        raise HTTPException(status_code=503, detail=f"Face model not available: {exc}. No photo or embedding was stored.")
    person.embeddings.append(FaceEmbedding(embedding=json.dumps(emb)))
    db.commit()
    log(db, "person_enrolled", user.id, f"person:{person_id}")
    return {"person_id": person_id, "enrolled": 1, "faces_detected": len(boxes)}

@router.delete("/people/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    """Full deletion on request: person + all face embeddings + their
    attendance records are removed, and the deletion is audit-logged."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.query(Attendance).filter(Attendance.person_id == person_id).delete()
    db.delete(person); db.commit()
    log(db, "person_deleted_all_face_data", user.id, f"person:{person_id}")
    return {"deleted": person_id, "face_data_deleted": True}
