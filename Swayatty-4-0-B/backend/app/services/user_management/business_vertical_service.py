from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_management.business_vertical import BusinessVertical
from app.schemas.user_management.business_vertical import (
    BusinessVerticalCreate,
    BusinessVerticalUpdate
)

def create_business_vertical(db: Session, vertical_data: BusinessVerticalCreate):
    vertical = BusinessVertical(**vertical_data.dict())
    db.add(vertical)
    db.commit()
    db.refresh(vertical)
    return vertical

def get_all_business_verticals(db: Session, skip: int = 0, limit: int = 10):
    return db.query(BusinessVertical).filter(BusinessVertical.is_deleted == False).offset(skip).limit(limit).all()

def get_business_vertical_by_id(db: Session, vertical_id: int):
    vertical = db.query(BusinessVertical).filter(
        BusinessVertical.id == vertical_id,
        BusinessVertical.is_deleted == False
    ).first()
    if not vertical:
        raise HTTPException(status_code=404, detail="Business Vertical not found")
    return vertical

def update_business_vertical(db: Session, vertical_id: int, vertical_data: BusinessVerticalUpdate):
    vertical = get_business_vertical_by_id(db, vertical_id)
    for key, value in vertical_data.dict(exclude_unset=True).items():
        setattr(vertical, key, value)
    db.commit()
    db.refresh(vertical)
    return vertical

def delete_business_vertical(db: Session, vertical_id: int):
    vertical = get_business_vertical_by_id(db, vertical_id)
    vertical.is_deleted = True
    db.commit()
    return vertical
