"""Create the first admin/teacher user. Usage:
python scripts_create_admin.py "Admin Name" admin@example.com secret-password teacher
No default password is shipped with this project."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from api.services.db import init_db, SessionLocal
from api.services.auth import hash_password
from api.models.models import User

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__); sys.exit(2)
    _, name, email, password, role = sys.argv
    assert role in ("admin", "teacher"), "role must be admin or teacher"
    init_db(); db = SessionLocal()
    if db.query(User).filter(User.email == email).first():
        print("User already exists."); sys.exit(0)
    db.add(User(name=name, email=email, password_hash=hash_password(password), role=role))
    db.commit(); print(f"Created {role}: {email}")
