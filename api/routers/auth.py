from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.services.db import get_db
from api.services.auth import verify_password, create_token
from api.models.models import User
from api.schemas.schemas import LoginIn

router = APIRouter()

@router.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": create_token(user),
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}
