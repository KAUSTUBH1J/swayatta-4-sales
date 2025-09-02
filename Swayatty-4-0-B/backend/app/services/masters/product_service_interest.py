from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional, Dict, Any

from app.models.masters.product_service_interest import ProductServiceInterest
from app.schemas.masters.product_service_interest import (
    ProductServiceInterestCreate,
    ProductServiceInterestUpdate
)


# ---------------- Mapper ----------------
def map_product_service_interest(ps: ProductServiceInterest) -> Optional[Dict[str, Any]]:
    if not ps:
        return None
    return {
        "id": ps.id,
        "name": ps.name,
        "description": ps.description,
        "is_active": ps.is_active,
        "is_deleted": ps.is_deleted,
        "created_by": ps.created_by,
        "updated_by": ps.updated_by,
        "created_at": ps.created_at,
        "updated_at": ps.updated_at,
        "created_by_name": ps.created_user.full_name if ps.created_user else None,
        "updated_by_name": ps.updated_user.full_name if ps.updated_user else None
    }


# ---------------- Create ----------------
def create_product_service_interest(db: Session, ps_data: ProductServiceInterestCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing = db.query(ProductServiceInterest).filter(
            func.lower(ProductServiceInterest.name) == ps_data.name.lower(),
            ProductServiceInterest.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Product/Service Interest '{ps_data.name}' already exists."
            )

        db_obj = ProductServiceInterest(
            name=ps_data.name.strip(),
            description=ps_data.description,
            is_active=ps_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return map_product_service_interest(db_obj)

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        import traceback; print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database error while creating Product/Service Interest")
    except Exception:
        db.rollback()
        import traceback; print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Product/Service Interest")


# ---------------- Get List ----------------
def get_product_service_interests(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(ProductServiceInterest).filter(ProductServiceInterest.is_deleted == False)

        if search:
            query = query.filter(or_(
                ProductServiceInterest.name.ilike(f"%{search}%"),
                ProductServiceInterest.description.ilike(f"%{search}%")
            ))

        total = query.count()
        records = query.order_by(ProductServiceInterest.id.asc()).offset(skip).limit(limit).all()

        return {
            "product_service_interests": [map_product_service_interest(ps) for ps in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch product/service interests")


# ---------------- Get by ID ----------------
def get_product_service_interest_by_id(db: Session, ps_id: int):
    try:
        record = db.query(ProductServiceInterest).filter(
            ProductServiceInterest.id == ps_id,
            ProductServiceInterest.is_deleted == False
        ).first()
        return map_product_service_interest(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch product/service interest")


# ---------------- Update ----------------
def update_product_service_interest(db: Session, ps_id: int, data: ProductServiceInterestUpdate, login_id: int):
    try:
        db_obj = db.query(ProductServiceInterest).filter(
            ProductServiceInterest.id == ps_id,
            ProductServiceInterest.is_deleted == False
        ).first()
        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_product_service_interest(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update product/service interest")


# ---------------- Delete (Soft) ----------------
def delete_product_service_interest(db: Session, ps_id: int, login_id: int):
    try:
        db_obj = db.query(ProductServiceInterest).filter(
            ProductServiceInterest.id == ps_id,
            ProductServiceInterest.is_deleted == False
        ).first()
        if not db_obj:
            return None

        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)

        return map_product_service_interest(db_obj)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete product/service interest")
