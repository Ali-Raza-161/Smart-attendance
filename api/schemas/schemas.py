from pydantic import BaseModel
from typing import Optional, List

class LoginIn(BaseModel):
    email: str
    password: str

class ClassIn(BaseModel):
    name: str
    teacher_id: Optional[int] = None

class PersonIn(BaseModel):
    name: str
    roll_or_employee_no: str
    class_id: Optional[int] = None
    status: str = "active"
    consent: bool = False

class SessionIn(BaseModel):
    class_id: int
    date: str
    start_time: Optional[str] = None

class AttendancePatch(BaseModel):
    status: str  # present | absent | late
