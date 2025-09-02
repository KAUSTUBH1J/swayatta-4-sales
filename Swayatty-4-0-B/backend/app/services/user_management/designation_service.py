from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import Optional, Dict, Any
from sqlalchemy import or_, func
from app.models.user_management.designation import Designation
from app.schemas.user_management.designation import DesignationCreate, DesignationUpdate

# ---------------- Utility ----------------
def map_designation_with_names(designation: Designation) -> Optional[Dict[str, Any]]:
    if not designation:
        return None

    return {
        "id": designation.id,
        "name": designation.name,   # 👈 updated
        "description": designation.description,
        "is_active": designation.is_active,
        "is_deleted": designation.is_deleted,
        "created_by": designation.created_by,
        "updated_by": designation.updated_by,
        "created_at": designation.created_at,
        "updated_at": designation.updated_at,
        "created_by_name": designation.created_user.full_name if designation.created_user else None,
        "updated_by_name": designation.updated_user.full_name if designation.updated_user else None
    }

# ---------------- Create ----------------
def create_designation(db: Session, designation_data: DesignationCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive, only non-deleted)
        existing_designation = db.query(Designation).filter(
            func.lower(Designation.name) == designation_data.name.lower(),
            Designation.is_deleted == False
        ).first()

        if existing_designation:
            raise HTTPException(
                status_code=400,
                detail=f"Designation '{designation_data.name}' already exists."
            )

        # Save new designation
        new_designation = Designation(
            name=designation_data.name.strip(),   # 👈 updated
            description=designation_data.description,
            is_active=designation_data.is_active,
            is_deleted=designation_data.is_deleted or False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(new_designation)
        db.commit()
        db.refresh(new_designation)

        return map_designation_with_names(new_designation)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create Designation):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while creating designation")

    except Exception as e:
        db.rollback()
        print("Unexpected Error (Create Designation):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while creating designation")

# ---------------- Get All ----------------
def get_designations(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> dict:
    try:
        query = db.query(Designation).filter(
            Designation.is_deleted == False
        )

        if search:
            query = query.filter(
                or_(
                    Designation.name.ilike(f"%{search}%"),
                    Designation.description.ilike(f"%{search}%")
                )
            )

        total = query.count()
        designations = query.order_by(Designation.id.asc()).offset(skip).limit(limit).all()
        data = [map_designation_with_names(d) for d in designations]

        return {
            "designations": data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }

    except SQLAlchemyError as e:
        print("DB Error (Get Designations):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while fetching designations")
    except Exception as e:
        print("Unexpected Error (Get Designations):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while fetching designations")

# ---------------- Get by ID ----------------
def get_designation_by_id(db: Session, designation_id: int) -> Optional[Dict[str, Any]]:
    try:
        designation = db.query(Designation).filter(
            Designation.id == designation_id,
            Designation.is_deleted == False
        ).first()
        return map_designation_with_names(designation)
    except SQLAlchemyError as e:
        print("DB Error (Get Designation by ID):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while fetching designation")
    except Exception as e:
        print("Unexpected Error (Get Designation by ID):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while fetching designation")

# ---------------- Update ----------------
def update_designation(db: Session, designation_id: int, designation_data: DesignationUpdate, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_designation = db.query(Designation).filter(
            Designation.id == designation_id,
            Designation.is_deleted == False
        ).first()
        if not db_designation:
            return None

        update_data = designation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_designation, field, value)

        db_designation.updated_by = login_id
        db.commit()
        db.refresh(db_designation)
        return map_designation_with_names(db_designation)

    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Update Designation):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while updating designation")
    except Exception as e:
        db.rollback()
        print("Unexpected Error (Update Designation):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while updating designation")

# ---------------- Soft Delete ----------------
def delete_designation(db: Session, designation_id: int, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_designation = db.query(Designation).filter(
            Designation.id == designation_id,
            Designation.is_deleted == False
        ).first()
        if not db_designation:
            return None

        db_designation.is_deleted = True
        db_designation.updated_by = login_id
        db.commit()
        db.refresh(db_designation)
        return map_designation_with_names(db_designation)

    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Delete Designation):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while deleting designation")
    except Exception as e:
        db.rollback()
        print("Unexpected Error (Delete Designation):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while deleting designation")
