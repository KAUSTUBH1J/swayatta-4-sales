from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_countries import MasterCountries
from app.schemas.masters.master_countries import MasterCountryCreate, MasterCountryUpdate


# ---------------- Mapper ----------------
def map_country(country: MasterCountries) -> Optional[Dict[str, Any]]:
    if not country:
        return None
    return {
        "id": country.id,
        "name": country.name,
        "description": country.description,
        "is_active": country.is_active,
        "is_deleted": country.is_deleted,
        "created_by": country.created_by,
        "updated_by": country.updated_by,
        "created_at": country.created_at,
        "updated_at": country.updated_at,
        "created_by_name": country.created_user.full_name if country.created_user else None,
        "updated_by_name": country.updated_user.full_name if country.updated_user else None
    }


# ---------------- Create ----------------
def create_country(db: Session, c_data: MasterCountryCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_country = db.query(MasterCountries).filter(
            func.lower(MasterCountries.name) == c_data.name.lower(),
            MasterCountries.is_deleted == False
        ).first()

        if existing_country:
            raise HTTPException(
                status_code=400,
                detail=f"Country '{c_data.name}' already exists."
            )

        db_country = MasterCountries(
            name=c_data.name.strip(),
            description=c_data.description,
            is_active=c_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_country)
        db.commit()
        db.refresh(db_country)

        return map_country(db_country)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Country")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Country")


# ---------------- Get List ----------------
def get_countries(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterCountries).filter(MasterCountries.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterCountries.name.ilike(f"%{search}%"),
                MasterCountries.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterCountries.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_countries": [map_country(c) for c in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch countries")


# ---------------- Get by ID ----------------
def get_country_by_id(db: Session, c_id: int):
    try:
        record = db.query(MasterCountries).filter(
            MasterCountries.id == c_id,
            MasterCountries.is_deleted == False
        ).first()
        return map_country(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch country")


# ---------------- Update ----------------
def update_country(db: Session, c_id: int, data: MasterCountryUpdate, login_id: int):
    try:
        db_obj = db.query(MasterCountries).filter(
            MasterCountries.id == c_id,
            MasterCountries.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_country(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update country")


# ---------------- Delete (Soft) ----------------
def delete_country(db: Session, c_id: int, login_id: int):
    try:
        db_obj = db.query(MasterCountries).filter(
            MasterCountries.id == c_id,
            MasterCountries.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_country(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete country")
