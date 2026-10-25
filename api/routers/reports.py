import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from api.services.db import get_db
from api.services.auth import require_role
from api.models.models import Attendance, Person, Session as AttSession

router = APIRouter()

def _rows(db, class_id=None, date_from=None, date_to=None, person_id=None):
    q = db.query(Attendance, Person, AttSession).join(Person, Person.id == Attendance.person_id).join(AttSession, AttSession.id == Attendance.session_id)
    if class_id: q = q.filter(AttSession.class_id == class_id)
    if date_from: q = q.filter(AttSession.date >= date_from)
    if date_to: q = q.filter(AttSession.date <= date_to)
    if person_id: q = q.filter(Attendance.person_id == person_id)
    out = []
    for att, person, sess in q.all():
        out.append({"attendance_id": att.id, "person_id": person.id, "name": person.name,
                    "roll_or_employee_no": person.roll_or_employee_no, "class_id": sess.class_id,
                    "date": sess.date, "status": att.status, "confidence": att.confidence})
    return out

@router.get("/reports/attendance")
def report(class_id: int = None, date_from: str = None, date_to: str = None, person_id: int = None,
           db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    rows = _rows(db, class_id, date_from, date_to, person_id)
    total = len(rows)
    present = sum(1 for r in rows if r["status"] == "present")
    return {"total": total, "present": present,
            "percentage": round(100 * present / total, 2) if total else 0.0, "rows": rows}

@router.get("/reports/export")
def export(class_id: int = None, date_from: str = None, date_to: str = None,
           db: Session = Depends(get_db), user=Depends(require_role("admin", "teacher"))):
    rows = _rows(db, class_id, date_from, date_to)
    try:
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Attendance"
        ws.append(["Name", "Roll/Employee No", "Class", "Date", "Status"])
        for r in rows:
            ws.append([r["name"], r["roll_or_employee_no"], r["class_id"], r["date"], r["status"]])
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=attendance.xlsx"})
    except ImportError:
        text = "Name,Roll,Class,Date,Status\n" + "\n".join(
            f'{r["name"]},{r["roll_or_employee_no"]},{r["class_id"]},{r["date"]},{r["status"]}' for r in rows)
        return StreamingResponse(io.BytesIO(text.encode()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=attendance.csv"})
