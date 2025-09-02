from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_partner_type import MasterPartnerTypes
from app.schemas.masters.partner_type import PartnerTypeCreate, PartnerTypeUpdate


# ---------------- Mapper ----------------
def map_partner_type(pt: MasterPartnerTypes) -> Optional[Dict[str, Any]]:
    if not pt:
        return None
    return {
        "id": pt.id,
        "name": pt.name,
        "description": pt.description,
        "is_active": pt.is_active,
        "is_deleted": pt.is_deleted,
        "created_by": pt.created_by,
        "updated_by": pt.updated_by,
        "created_at": pt.created_at,
        "updated_at": pt.updated_at,
        "created_by_name": pt.created_user.full_name if pt.created_user else None,
        "updated_by_name": pt.updated_user.full_name if pt.updated_user else None
    }


# ---------------- Create ----------------
def create_partner_type(db: Session, pt_data: PartnerTypeCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_pt = db.query(MasterPartnerTypes).filter(
            func.lower(MasterPartnerTypes.name) == pt_data.name.lower(),
            MasterPartnerTypes.is_deleted == False
        ).first()

        if existing_pt:
            raise HTTPException(
                status_code=400,
                detail=f"Partner Type '{pt_data.name}' already exists."
            )

        db_pt = MasterPartnerTypes(
            name=pt_data.name.strip(),
            description=pt_data.description,
            is_active=pt_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_pt)
        db.commit()
        db.refresh(db_pt)

        return map_partner_type(db_pt)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Partner Type")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Partner Type")


# ---------------- Get List ----------------
def get_partner_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterPartnerTypes).filter(MasterPartnerTypes.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterPartnerTypes.name.ilike(f"%{search}%"),
                MasterPartnerTypes.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterPartnerTypes.id.asc()).offset(skip).limit(limit).all()

        return {
            "partner_types": [map_partner_type(pt) for pt in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch partner types")


# ---------------- Get by ID ----------------
def get_partner_type_by_id(db: Session, pt_id: int):
    try:
        record = db.query(MasterPartnerTypes).filter(
            MasterPartnerTypes.id == pt_id,
            MasterPartnerTypes.is_deleted == False
        ).first()
        return map_partner_type(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch partner type")


# ---------------- Update ----------------
def update_partner_type(db: Session, pt_id: int, data: PartnerTypeUpdate, login_id: int):
    try:
        db_obj = db.query(MasterPartnerTypes).filter(
            MasterPartnerTypes.id == pt_id,
            MasterPartnerTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_partner_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update partner type")


# ---------------- Delete (Soft) ----------------
def delete_partner_type(db: Session, pt_id: int, login_id: int):
    try:
        db_obj = db.query(MasterPartnerTypes).filter(
            MasterPartnerTypes.id == pt_id,
            MasterPartnerTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_partner_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete partner type")
