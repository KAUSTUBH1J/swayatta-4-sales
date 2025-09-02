from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_account_types import MasterAccountTypes
from app.schemas.masters.master_account_types import MasterAccountTypeCreate, MasterAccountTypeUpdate


# ---------------- Mapper ----------------
def map_account_type(at: MasterAccountTypes) -> Optional[Dict[str, Any]]:
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
def create_account_type(db: Session, at_data: MasterAccountTypeCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_at = db.query(MasterAccountTypes).filter(
            func.lower(MasterAccountTypes.name) == at_data.name.lower(),
            MasterAccountTypes.is_deleted == False
        ).first()

        if existing_at:
            raise HTTPException(
                status_code=400,
                detail=f"Account Type '{at_data.name}' already exists."
            )

        db_at = MasterAccountTypes(
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

        return map_account_type(db_at)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Account Type")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Account Type")


# ---------------- Get List ----------------
def get_account_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterAccountTypes).filter(MasterAccountTypes.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterAccountTypes.name.ilike(f"%{search}%"),
                MasterAccountTypes.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterAccountTypes.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_account_types": [map_account_type(at) for at in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch account types")


# ---------------- Get by ID ----------------
def get_account_type_by_id(db: Session, at_id: int):
    try:
        record = db.query(MasterAccountTypes).filter(
            MasterAccountTypes.id == at_id,
            MasterAccountTypes.is_deleted == False
        ).first()
        return map_account_type(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch account type")


# ---------------- Update ----------------
def update_account_type(db: Session, at_id: int, data: MasterAccountTypeUpdate, login_id: int):
    try:
        db_obj = db.query(MasterAccountTypes).filter(
            MasterAccountTypes.id == at_id,
            MasterAccountTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_account_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update account type")


# ---------------- Delete (Soft) ----------------
def delete_account_type(db: Session, at_id: int, login_id: int):
    try:
        db_obj = db.query(MasterAccountTypes).filter(
            MasterAccountTypes.id == at_id,
            MasterAccountTypes.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_account_type(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete account type")
