from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_cities import MasterCities
from app.schemas.masters.master_cities import MasterCityCreate, MasterCityUpdate


# ---------------- Mapper ----------------
def map_city(city: MasterCities) -> Optional[Dict[str, Any]]:
    if not city:
        return None
    return {
        "id": city.id,
        "name": city.name,
        "description": city.description,
        "is_active": city.is_active,
        "is_deleted": city.is_deleted,
        "created_by": city.created_by,
        "updated_by": city.updated_by,
        "created_at": city.created_at,
        "updated_at": city.updated_at,
        "created_by_name": city.created_user.full_name if city.created_user else None,
        "updated_by_name": city.updated_user.full_name if city.updated_user else None
    }


# ---------------- Create ----------------
def create_city(db: Session, c_data: MasterCityCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_city = db.query(MasterCities).filter(
            func.lower(MasterCities.name) == c_data.name.lower(),
            MasterCities.is_deleted == False
        ).first()

        if existing_city:
            raise HTTPException(
                status_code=400,
                detail=f"City '{c_data.name}' already exists."
            )

        db_city = MasterCities(
            name=c_data.name.strip(),
            description=c_data.description,
            is_active=c_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_city)
        db.commit()
        db.refresh(db_city)

        return map_city(db_city)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating City")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating City")


# ---------------- Get List ----------------
def get_cities(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(MasterCities).filter(MasterCities.is_deleted == False)

        if search:
            query = query.filter(or_(
                MasterCities.name.ilike(f"%{search}%"),
                MasterCities.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(MasterCities.id.asc()).offset(skip).limit(limit).all()

        return {
            "master_cities": [map_city(c) for c in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch cities")


# ---------------- Get by ID ----------------
def get_city_by_id(db: Session, c_id: int):
    try:
        record = db.query(MasterCities).filter(
            MasterCities.id == c_id,
            MasterCities.is_deleted == False
        ).first()
        return map_city(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch city")


# ---------------- Update ----------------
def update_city(db: Session, c_id: int, data: MasterCityUpdate, login_id: int):
    try:
        db_obj = db.query(MasterCities).filter(
            MasterCities.id == c_id,
            MasterCities.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_city(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update city")


# ---------------- Delete (Soft) ----------------
def delete_city(db: Session, c_id: int, login_id: int):
    try:
        db_obj = db.query(MasterCities).filter(
            MasterCities.id == c_id,
            MasterCities.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_city(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete city")
