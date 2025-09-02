from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_address_type import MasterAddresssTypes
from app.schemas.masters.master_address_type import MasterAddressTypeCreate, MasterAddressTypeUpdate


# ---------------- Mapper ----------------
def map_address_type(at: MasterAddresssTypes) -> Optional[Dict[str, Any]]:
    if not at:
        return None
    return {
        "id": at.id,
        "name": at.name,
        "description": at.description,
        "is_active": at.is_active,
        "is_deleted": at.is_deleted,
        "created_by": at.created_by,
        "updated_by": at.updated_by,
        "created_at": at.created_at,
        "updated_at": at.updated_at,
        "created_by_name": at.created_user.full_name if at.created_user else None,
        "updated_by_name": at.updated_user.full_name if at.updated_user else None
    }


# ---------------- Create ----------------
def create_address_type(db: Session, at_data: MasterAddressTypeCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_at = db.query(MasterAddresssTypes).filter(
            func.lower(MasterAddresssTypes.name) == at_data.name.lower(),
            MasterAddresssTypes.is_deleted == False
        ).first()

        if existing_at:
            raise HTTPException(
                status_code=400,
                detail=f"Address Type '{at_data.name}' already exists."
            )

        db_at = MasterAddresssTypes(
            name=at_data.name.strip(),
            description=at_data.description,
            is_active=at_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_at)
        db.commit()
        db.refresh(db_at)

        return map_address_type(db_at)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Address Type")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Address Type")


# ---------------- Get List ----------------
def get_address_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterAddresssTypes).filter(MasterAddresssTypes.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterAddresssTypes.name.ilike(f"%{search}%"),
                MasterAddresssTypes.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterAddresssTypes.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_address_types": [map_address_type(at) for at in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch address types")


# ---------------- Get by ID ----------------
def get_address_type_by_id(db: Session, at_id: int):
    try:
        record = db.query(MasterAddresssTypes).filter(
            MasterAddresssTypes.id == at_id,
            MasterAddresssTypes.is_deleted == False
        ).first()
        return map_address_type(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch address type")


# ---------------- Update ----------------
def update_address_type(db: Session, at_id: int, data: MasterAddressTypeUpdate, login_id: int):
    try:
        db_obj = db.query(MasterAddresssTypes).filter(
            MasterAddresssTypes.id == at_id,
            MasterAddresssTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_address_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update address type")


# ---------------- Delete (Soft) ----------------
def delete_address_type(db: Session, at_id: int, login_id: int):
    try:
        db_obj = db.query(MasterAddresssTypes).filter(
            MasterAddresssTypes.id == at_id,
            MasterAddresssTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_address_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete address type")
