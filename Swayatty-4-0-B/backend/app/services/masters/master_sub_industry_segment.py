from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_sub_industry_segment import MasterSubIndustrySegments
from app.schemas.masters.master_sub_industry_segment import (
    MasterSubIndustrySegmentCreate,
    MasterSubIndustrySegmentUpdate
)


# ---------------- Mapper ----------------
def map_master_sub_industry_segment(msis: MasterSubIndustrySegments) -> Optional[Dict[str, Any]]:
    if not msis:
        return None
    return {
        "id": msis.id,
        "name": msis.name,
        "description": msis.description,
        "is_active": msis.is_active,
        "is_deleted": msis.is_deleted,
        "created_by": msis.created_by,
        "updated_by": msis.updated_by,
        "created_at": msis.created_at,
        "updated_at": msis.updated_at,
        "created_by_name": msis.created_user.full_name if msis.created_user else None,
        "updated_by_name": msis.updated_user.full_name if msis.updated_user else None
    }


# ---------------- Create ----------------
def create_master_sub_industry_segment(db: Session, data: MasterSubIndustrySegmentCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing = db.query(MasterSubIndustrySegments).filter(
            func.lower(MasterSubIndustrySegments.name) == data.name.lower(),
            MasterSubIndustrySegments.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Sub Industry Segment '{data.name}' already exists."
            )

        db_obj = MasterSubIndustrySegments(
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

        return map_master_sub_industry_segment(db_obj)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Sub Industry Segment")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Sub Industry Segment")


# ---------------- Get List ----------------
def get_master_sub_industry_segments(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterSubIndustrySegments).filter(MasterSubIndustrySegments.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterSubIndustrySegments.name.ilike(f"%{search}%"),
                MasterSubIndustrySegments.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterSubIndustrySegments.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_sub_industry_segments": [map_master_sub_industry_segment(msis) for msis in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch Sub Industry Segments")


# ---------------- Get by ID ----------------
def get_master_sub_industry_segment_by_id(db: Session, msis_id: int):
    try:
        record = db.query(MasterSubIndustrySegments).filter(
            MasterSubIndustrySegments.id == msis_id,
            MasterSubIndustrySegments.is_deleted == False
        ).first()
        return map_master_sub_industry_segment(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch Sub Industry Segment")


# ---------------- Update ----------------
def update_master_sub_industry_segment(db: Session, msis_id: int, data: MasterSubIndustrySegmentUpdate, login_id: int):
    try:
        db_obj = db.query(MasterSubIndustrySegments).filter(
            MasterSubIndustrySegments.id == msis_id,
            MasterSubIndustrySegments.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_master_sub_industry_segment(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update Sub Industry Segment")


# ---------------- Delete (Soft) ----------------
def delete_master_sub_industry_segment(db: Session, msis_id: int, login_id: int):
    try:
        db_obj = db.query(MasterSubIndustrySegments).filter(
            MasterSubIndustrySegments.id == msis_id,
            MasterSubIndustrySegments.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_master_sub_industry_segment(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete Sub Industry Segment")
