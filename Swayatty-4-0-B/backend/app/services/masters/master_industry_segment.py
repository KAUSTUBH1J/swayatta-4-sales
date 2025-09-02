from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_industry_segment import MasterIndustrySegments
from app.schemas.masters.master_industry_segment import (
    MasterIndustrySegmentCreate,
    MasterIndustrySegmentUpdate
)


# ---------------- Mapper ----------------
def map_master_industry_segment(mis: MasterIndustrySegments) -> Optional[Dict[str, Any]]:
    if not mis:
        return None
    return {
        "id": mis.id,
        "name": mis.name,
        "description": mis.description,
        "is_active": mis.is_active,
        "is_deleted": mis.is_deleted,
        "created_by": mis.created_by,
        "updated_by": mis.updated_by,
        "created_at": mis.created_at,
        "updated_at": mis.updated_at,
        "created_by_name": mis.created_user.full_name if mis.created_user else None,
        "updated_by_name": mis.updated_user.full_name if mis.updated_user else None
    }


# ---------------- Create ----------------
def create_master_industry_segment(db: Session, data: MasterIndustrySegmentCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing = db.query(MasterIndustrySegments).filter(
            func.lower(MasterIndustrySegments.name) == data.name.lower(),
            MasterIndustrySegments.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Industry Segment '{data.name}' already exists."
            )

        db_obj = MasterIndustrySegments(
            name=data.name.strip(),
            description=data.description,
            is_active=data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return map_master_industry_segment(db_obj)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Industry Segment")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Industry Segment")


# ---------------- Get List ----------------
def get_master_industry_segments(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterIndustrySegments).filter(MasterIndustrySegments.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterIndustrySegments.name.ilike(f"%{search}%"),
                MasterIndustrySegments.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterIndustrySegments.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_industry_segments": [map_master_industry_segment(mis) for mis in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch Industry Segments")


# ---------------- Get by ID ----------------
def get_master_industry_segment_by_id(db: Session, mis_id: int):
    try:
        record = db.query(MasterIndustrySegments).filter(
            MasterIndustrySegments.id == mis_id,
            MasterIndustrySegments.is_deleted == False
        ).first()
        return map_master_industry_segment(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch Industry Segment")


# ---------------- Update ----------------
def update_master_industry_segment(db: Session, mis_id: int, data: MasterIndustrySegmentUpdate, login_id: int):
    try:
        db_obj = db.query(MasterIndustrySegments).filter(
            MasterIndustrySegments.id == mis_id,
            MasterIndustrySegments.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_master_industry_segment(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update Industry Segment")


# ---------------- Delete (Soft) ----------------
def delete_master_industry_segment(db: Session, mis_id: int, login_id: int):
    try:
        db_obj = db.query(MasterIndustrySegments).filter(
            MasterIndustrySegments.id == mis_id,
            MasterIndustrySegments.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_master_industry_segment(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete Industry Segment")
