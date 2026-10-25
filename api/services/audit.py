from sqlalchemy.orm import Session
from api.models.models import AuditLog

def log(db: Session, action: str, user_id=None, target=None):
    db.add(AuditLog(action=action, user_id=user_id, target=target))
    db.commit()
