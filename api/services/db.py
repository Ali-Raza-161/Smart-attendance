"""Database session. Postgres via DATABASE_URL when set, otherwise a
local SQLite file (attendance.db, gitignored). Live Postgres was NOT
tested in this build."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./attendance.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
