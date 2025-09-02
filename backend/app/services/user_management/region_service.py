from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_management.region import Region
from app.schemas.user_management.region import RegionCreate, RegionUpdate

def create_region(db: Session, region_data: RegionCreate):
    region = Region(**region_data.dict())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region

def get_all_regions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Region).filter(Region.is_deleted == False).offset(skip).limit(limit).all()

def get_region_by_id(db: Session, region_id: int):
    region = db.query(Region).filter(Region.id == region_id, Region.is_deleted == False).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

def update_region(db: Session, region_id: int, region_data: RegionUpdate):
    region = get_region_by_id(db, region_id)
    for key, value in region_data.dict(exclude_unset=True).items():
        setattr(region, key, value)
    db.commit()
    db.refresh(region)
    return region

def delete_region(db: Session, region_id: int):
    region = get_region_by_id(db, region_id)
    region.is_deleted = True
    db.commit()
    return region
