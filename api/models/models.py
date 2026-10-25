"""SQLAlchemy models. Embeddings are stored as JSON arrays of floats.

In PostgreSQL production, the embedding column can be migrated to
pgvector; the API code treats it as a list of floats either way.
Live Postgres was not tested in this build (SQLite fallback, see README).
"""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

def _now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="teacher")  # admin | teacher
    created_at = Column(DateTime, default=_now)

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=_now)

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    roll_or_employee_no = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    status = Column(String, default="active")
    consent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)
    embeddings = relationship("FaceEmbedding", cascade="all, delete-orphan", back_populates="person")

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    embedding = Column(Text, nullable=False)  # JSON list of 512 floats
    created_at = Column(DateTime, default=_now)
    person = relationship("Person", back_populates="embeddings")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(String, nullable=False)
    start_time = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=_now)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    status = Column(String, default="absent")  # present | absent | late
    confidence = Column(Float, nullable=True)
    marked_at = Column(DateTime, default=_now)
    marked_by = Column(String, default="teacher")  # system | teacher

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    user_id = Column(Integer, nullable=True)
    target = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now)
