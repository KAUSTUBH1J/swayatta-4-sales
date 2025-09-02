from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.company_type import CompanyTypeMaster
from app.schemas.masters.company_type import CompanyTypeCreate, CompanyTypeUpdate
from fastapi import FastAPI,status
from sqlalchemy import func

def map_company_type(bv: CompanyTypeMaster) -> Optional[Dict[str, Any]]:
    if not bv:
        return None
    return {
        "id": bv.id,
        "name": bv.name,
        "description": bv.description,
        "is_active": bv.is_active,
        "is_deleted": bv.is_deleted,
        "created_by": bv.created_by,
        "updated_by": bv.updated_by,
        "created_at": bv.created_at,
        "updated_at": bv.updated_at,
        "created_by_name": bv.created_user.full_name if bv.created_user else None,
        "updated_by_name": bv.updated_user.full_name if bv.updated_user else None
    }

def create_company_type(db: Session, bv_data: CompanyTypeCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_bv = db.query(CompanyTypeMaster).filter(
            func.lower(CompanyTypeMaster.name) == bv_data.name.lower(),
            CompanyTypeMaster.is_deleted == False
        ).first()

        if existing_bv:
            raise HTTPException(
                status_code=400,
                detail=f"Company Type '{bv_data.name}' already exists."
            )

        # Save exactly as entered (strip only spaces)
        db_bv = CompanyTypeMaster(
            name=bv_data.name.strip(),
            description=bv_data.description,
            is_active=bv_data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_bv)
        db.commit()
        db.refresh(db_bv)

        return map_company_type(db_bv)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        import traceback
        print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error while creating Company Type")

    except Exception as e:
        db.rollback()
        import traceback
        print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Company Type")
#-------------------Get CompanyType---------------------------------------
def get_company_types(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(CompanyTypeMaster).filter(
            CompanyTypeMaster.is_deleted == False
            
        )
        if search:
            query = query.filter(or_(
                CompanyTypeMaster.name.ilike(f"%{search}%"),
                CompanyTypeMaster.description.ilike(f"%{search}%")
            ))
        total = query.count()
        records = query.order_by(CompanyTypeMaster.id.asc()).offset(skip).limit(limit).all()
        return {
            "company_types": [map_company_type(bv) for bv in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch business verticals")

#----------------Get CompanyType by Id-------------------------------------
def get_company_type_by_id(db: Session, bv_id: int):
    try:
        record = db.query(CompanyTypeMaster).filter(
            CompanyTypeMaster.id == bv_id,
            CompanyTypeMaster.is_deleted == False
           
        ).first()
        return map_company_type(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch business vertical")

def update_company_type(db: Session, bv_id: int, data: CompanyTypeUpdate, login_id: int):
    try:
        db_obj = db.query(CompanyTypeMaster).filter(CompanyTypeMaster.id == bv_id, CompanyTypeMaster.is_deleted == False).first()
        if not db_obj:
            return None
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)
        return map_company_type(db_obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update business vertical")

#-------------------Delete Company Type--------------------------------
def delete_company_type(db: Session, bv_id: int, login_id: int):
    try:
        db_obj = db.query(CompanyTypeMaster).filter(CompanyTypeMaster.id == bv_id, CompanyTypeMaster.is_deleted == False).first()
        if not db_obj:
            return None
        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)
        return map_company_type(db_obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete business vertical")
