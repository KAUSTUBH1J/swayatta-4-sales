from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.models.masters.region import Region
from app.schemas.masters.region import RegionCreate, RegionUpdate

# -------- Serializer --------
def serialize_region(region: Region) -> Dict[str, Any]:
    if not region:
        return None
    return {
        "id": region.id,
        "name": region.name,
        "description": region.description,
        "is_active": region.is_active,
        "is_deleted": region.is_deleted,
        "created_by": region.created_by,
        "updated_by": region.updated_by,
        "created_at": region.created_at,
        "updated_at": region.updated_at,
        "created_by_name": getattr(region.created_user, 'full_name', None),
        "updated_by_name": getattr(region.updated_user, 'full_name', None),
    }

# -------- Create Region with Duplicate Check --------
def create_region(db: Session, region_data: RegionCreate, login_id: int) -> Dict[str, Any]:
    try:
        # ===== Duplicate Name Check (Case-Insensitive) =====
        existing_region = db.query(Region).filter(
            func.lower(Region.name) == func.lower(region_data.name),
            Region.is_deleted == False
        ).first()
        if existing_region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region name '{region_data.name}' already exists."
            )

        db_region = Region(
            name=region_data.name,
            description=region_data.description,
            is_active=region_data.is_active if region_data.is_active is not None else True,
            is_deleted=False,
            created_by=login_id
        )
        db.add(db_region)
        db.commit()
        db.refresh(db_region)
        return serialize_region(db_region)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating region")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating region: {str(e)}")

# -------- Get Regions with search & pagination --------
def get_regions(db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None) -> Dict[str, Any]:
    try:
        query = db.query(Region).filter(
            Region.is_deleted == False
        )

        if search:
            query = query.filter(
                or_(
                    Region.name.ilike(f"%{search}%"),
                    Region.description.ilike(f"%{search}%")
                )
            )

        total = query.count()
        regions = query.order_by(Region.id.asc()).offset(skip).limit(limit).all()
        regions_data = [serialize_region(r) for r in regions]

        return {
            "regions": regions_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching regions")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regions: {str(e)}")

# -------- Get Region by ID --------
def get_region_by_id(db: Session, region_id: int) -> Optional[Dict[str, Any]]:
    try:
        region = db.query(Region).filter(
            Region.id == region_id,
            Region.is_deleted == False
        ).first()
        return serialize_region(region)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while fetching region by ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching region by ID: {str(e)}")

# -------- Update Region with Duplicate Check --------
def update_region(db: Session, region_id: int, region_data: RegionUpdate, login_id: int = None) -> Optional[Dict[str, Any]]:
    try:
        db_region = db.query(Region).filter(
            Region.id == region_id,
            Region.is_deleted == False
        ).first()
        if not db_region:
            return None

        update_data = region_data.dict(exclude_unset=True)

        # Duplicate check for name
        if "name" in update_data:
            existing_region = db.query(Region).filter(
                func.lower(Region.name) == func.lower(update_data["name"]),
                Region.id != region_id,
                Region.is_deleted == False
            ).first()
            if existing_region:
                raise HTTPException(status_code=400, detail=f"Region name '{update_data['name']}' already exists.")

        for field, value in update_data.items():
            setattr(db_region, field, value)

        if login_id:
            db_region.updated_by = login_id

        db.commit()
        db.refresh(db_region)
        return serialize_region(db_region)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating region")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating region: {str(e)}")

# -------- Soft Delete Region --------
def delete_region(db: Session, region_id: int, login_id: int = None) -> Optional[Dict[str, Any]]:
    try:
        db_region = db.query(Region).filter(
            Region.id == region_id,
            Region.is_deleted == False
        ).first()
        if not db_region:
            return None

        db_region.is_deleted = True
        if login_id:
            db_region.updated_by = login_id

        db.commit()
        db.refresh(db_region)
        return serialize_region(db_region)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting region")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting region: {str(e)}")
