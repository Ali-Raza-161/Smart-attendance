import os, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from api.services.db import get_db
from api.models.models import User

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def create_token(user: User) -> str:
    payload = {"sub": str(user.id), "email": user.email, "role": user.role,
               "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer),
                     db: Session = Depends(get_db)) -> User:
    if not creds:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles):
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Role not allowed")
        return user
    return _check
