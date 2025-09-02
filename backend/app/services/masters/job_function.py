from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.models.masters.master_job_function import JobFunction
from app.schemas.masters.job_function import JobFunctionCreate, JobFunctionUpdate
from fastapi import FastAPI,status
from sqlalchemy import func

def map_job_function(jf: JobFunction) -> Optional[Dict[str, Any]]:
    if not jf:
        return None
    return {
        "id": jf.id,
        "name": jf.name,
        "description": jf.description,
        "is_active": jf.is_active,
        "is_deleted": jf.is_deleted,
        "created_by": jf.created_by,
        "updated_by": jf.updated_by,
        "created_at": jf.created_at,
        "updated_at": jf.updated_at,
        "created_by_name": jf.created_user.full_name if jf.created_user else None,
        "updated_by_name": jf.updated_user.full_name if jf.updated_user else None
    }

def create_job_function(db: Session, bv_data: JobFunctionCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, not deleted)
        existing_bv = db.query(JobFunction).filter(
            func.lower(JobFunction.name) == bv_data.name.lower(),
            JobFunction.is_deleted == False
        ).first()

        if existing_bv:
            raise HTTPException(
                status_code=400,
                detail=f"Job Function'{bv_data.name}' already exists."
            )

        # Save exactly as entered (strip only spaces)
        db_bv = JobFunction(
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

        return map_job_function(db_bv)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        import traceback
        print("DB Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error while creating Job Function")

    except Exception as e:
        db.rollback()
        import traceback
        print("Unexpected Error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong while creating Job Function")
#-------------------Get JobFunction---------------------------------------
def get_job_functions(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    try:
        query = db.query(JobFunction).filter(
            JobFunction.is_deleted == False
            
        )
        if search:
            query = query.filter(or_(
                JobFunction.name.ilike(f"%{search}%"),
                JobFunction.description.ilike(f"%{search}%")
            ))
        total = query.count()
        records = query.order_by(JobFunction.id.asc()).offset(skip).limit(limit).all()
        return {
            "job_functions": [map_job_function(jf) for jf in records],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch job functions")

#----------------Get JobFunction by Id-------------------------------------
def get_job_function_by_id(db: Session, bv_id: int):
    try:
        record = db.query(JobFunction).filter(
            JobFunction.id == bv_id,
            JobFunction.is_deleted == False
           
        ).first()
        return map_job_function(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch job functions")

def update_job_function(db: Session, bv_id: int, data: JobFunctionUpdate, login_id: int):
    try:
        db_obj = db.query(JobFunction).filter(JobFunction.id == bv_id, JobFunction.is_deleted == False).first()
        if not db_obj:
            return None
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)
        return map_job_function(db_obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update job functions")

#-------------------Delete Job Function--------------------------------
def delete_job_function(db: Session, bv_id: int, login_id: int):
    try:
        db_obj = db.query(JobFunction).filter(JobFunction.id == bv_id, JobFunction.is_deleted == False).first()
        if not db_obj:
            return None
        db_obj.is_deleted = True
        db_obj.updated_by = login_id
        db.commit()
        db.refresh(db_obj)
        return map_job_function(db_obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete business vertical")
