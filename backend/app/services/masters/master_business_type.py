from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_business_types import MasterBusinessTypes
from app.schemas.masters.master_business_type import MasterBusinessTypeCreate, MasterBusinessTypeUpdate


# ---------------- Mapper ----------------
def map_business_type(bt: MasterBusinessTypes) -> Optional[Dict[str, Any]]:
    if not bt:
        return None
    return {
        "id": bt.id,
        "name": bt.name,
        "description": bt.description,
        "is_active": bt.is_active,
        "is_deleted": bt.is_deleted,
        "created_by": bt.created_by,
        "updated_by": bt.updated_by,
        "created_at": bt.created_at,
        "updated_at": bt.updated_at,
        "created_by_name": bt.created_user.full_name if bt.created_user else None,
        "updated_by_name": bt.updated_user.full_name if bt.updated_user else None
    }


# ---------------- Create ----------------
def create_business_type(db: Session, bt_data: MasterBusinessTypeCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_bt = db.query(MasterBusinessTypes).filter(
            func.lower(MasterBusinessTypes.name) == bt_data.name.lower(),
            MasterBusinessTypes.is_deleted == False
        ).first()

        if existing_bt:
            raise HTTPException(
                status_code=400,
                detail=f"Business Type '{bt_data.name}' already exists."
            )

        db_bt = MasterBusinessTypes(
            name=bt_data.name.strip(),
            description=bt_data.description,
            is_active=bt_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_bt)
        db.commit()
        db.refresh(db_bt)

        return map_business_type(db_bt)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Business Type")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Business Type")


# ---------------- Get List ----------------
def get_business_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterBusinessTypes).filter(MasterBusinessTypes.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterBusinessTypes.name.ilike(f"%{search}%"),
                MasterBusinessTypes.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterBusinessTypes.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_business_types": [map_business_type(bt) for bt in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch business types")


# ---------------- Get by ID ----------------
def get_business_type_by_id(db: Session, bt_id: int):
    try:
        record = db.query(MasterBusinessTypes).filter(
            MasterBusinessTypes.id == bt_id,
            MasterBusinessTypes.is_deleted == False
        ).first()
        return map_business_type(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch business type")


# ---------------- Update ----------------
def update_business_type(db: Session, bt_id: int, data: MasterBusinessTypeUpdate, login_id: int):
    try:
        db_obj = db.query(MasterBusinessTypes).filter(
            MasterBusinessTypes.id == bt_id,
            MasterBusinessTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_business_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update business type")


# ---------------- Delete (Soft) ----------------
def delete_business_type(db: Session, bt_id: int, login_id: int):
    try:
        db_obj = db.query(MasterBusinessTypes).filter(
            MasterBusinessTypes.id == bt_id,
            MasterBusinessTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_business_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete business type")
