from sqlalchemy.orm import Session
from app.models.user_management.audit_log import AuditLog
from app.schemas.user_management.audit_log import AuditLogCreate, AuditLogUpdate

def create_auditlog(db: Session, item: AuditLogCreate):
    db_item = AuditLog(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_auditlog(db: Session, item_id: int):
    return db.query(AuditLog).filter(AuditLog.id == item_id).first()

def get_auditlogs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(AuditLog).offset(skip).limit(limit).all()

def update_auditlog(db: Session, item_id: int, item: AuditLogUpdate):
    db_item = db.query(AuditLog).filter(AuditLog.id == item_id).first()
    if not db_item:
        return None
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_auditlog(db: Session, item_id: int):
    db_item = db.query(AuditLog).filter(AuditLog.id == item_id).first()
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
