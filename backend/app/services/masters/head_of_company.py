from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.head_of_company import HeadCompanyMaster
from app.schemas.masters.head_of_company import HeadCompanyCreate, HeadCompanyUpdate


# ---------------- Mapper ----------------
def map_head_company(hc: HeadCompanyMaster) -> Optional[Dict[str, Any]]:
    if not hc:
        return None
    return {
        "id": hc.id,
        "name": hc.name,
        "description": hc.description,
        "is_active": hc.is_active,
        "is_deleted": hc.is_deleted,
        "created_by": hc.created_by,
        "updated_by": hc.updated_by,
        "created_at": hc.created_at,
        "updated_at": hc.updated_at,
        "created_by_name": hc.created_user.full_name if hc.created_user else None,
        "updated_by_name": hc.updated_user.full_name if hc.updated_user else None
    }


# ---------------- Create ----------------
def create_head_company(db: Session, hc_data: HeadCompanyCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_hc = db.query(HeadCompanyMaster).filter(
            func.lower(HeadCompanyMaster.name) == hc_data.name.lower(),
            HeadCompanyMaster.is_deleted == False
        ).first()

        if existing_hc:
            raise HTTPException(
                status_code=400,
                detail=f"Head of Company '{hc_data.name}' already exists."
            )

        db_hc = HeadCompanyMaster(
            name=hc_data.name.strip(),
            description=hc_data.description,
            is_active=hc_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_hc)
        db.commit()
        db.refresh(db_hc)

        return map_head_company(db_hc)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Head of Company")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Head of Company")


# ---------------- Get List ----------------
def get_head_companies(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(HeadCompanyMaster).filter(HeadCompanyMaster.is_deleted == False)

        if search:
            query = query.filter(or_(
                HeadCompanyMaster.name.ilike(f"%{search}%"),
                HeadCompanyMaster.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(HeadCompanyMaster.id.asc()).offset(skip).limit(limit).all()

        return {
            "head_companies": [map_head_company(hc) for hc in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch head companies")


# ---------------- Get by ID ----------------
def get_head_company_by_id(db: Session, hc_id: int):
    try:
        record = db.query(HeadCompanyMaster).filter(
            HeadCompanyMaster.id == hc_id,
            HeadCompanyMaster.is_deleted == False
        ).first()
        return map_head_company(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch head company")


# ---------------- Update ----------------
def update_head_company(db: Session, hc_id: int, data: HeadCompanyUpdate, login_id: int):
    try:
        db_obj = db.query(HeadCompanyMaster).filter(
            HeadCompanyMaster.id == hc_id,
            HeadCompanyMaster.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_head_company(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update head company")


# ---------------- Delete (Soft) ----------------
def delete_head_company(db: Session, hc_id: int, login_id: int):
    try:
        db_obj = db.query(HeadCompanyMaster).filter(
            HeadCompanyMaster.id == hc_id,
            HeadCompanyMaster.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_head_company(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete head company")
