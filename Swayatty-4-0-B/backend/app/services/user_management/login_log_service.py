from sqlalchemy.orm import Session
from app.models.user_management.login_log import LoginLog
from app.schemas.user_management.login_log import LoginLogCreate, LoginLogUpdate

def create_loginlog(db: Session, item: LoginLogCreate):
    db_item = LoginLog(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_loginlog(db: Session, item_id: int):
    return db.query(LoginLog).filter(LoginLog.id == item_id).first()

def get_loginlogs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(LoginLog).offset(skip).limit(limit).all()

def update_loginlog(db: Session, item_id: int, item: LoginLogUpdate):
    db_item = db.query(LoginLog).filter(LoginLog.id == item_id).first()
    if not db_item:
        return None
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_loginlog(db: Session, item_id: int):
    db_item = db.query(LoginLog).filter(LoginLog.id == item_id).first()
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
