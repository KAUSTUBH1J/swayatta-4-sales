from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from fastapi import HTTPException
from typing import Optional, Dict, Any
from sqlalchemy import func
from fastapi import FastAPI,status
from app.models.user_management.department import Department
from app.schemas.user_management.department import (
    DepartmentCreate,
    DepartmentUpdate,
)

# -------- Helper: serialize single Department including created/updated user names --------
def serialize_department(dept: Department) -> Optional[Dict[str, Any]]:
    if not dept:
        return None

    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "is_active": dept.is_active,
        "is_deleted": dept.is_deleted,
        "created_by": dept.created_by,
        "updated_by": dept.updated_by,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
        "created_by_name": dept.created_user.full_name if dept.created_user else None,
        "updated_by_name": dept.updated_user.full_name if dept.updated_user else None,
    }

# -------- Create Department --------
def create_department(db: Session, dept_data: DepartmentCreate, login_id: int):
    try:
        # Duplicate check (case-insensitive by name, only non-deleted)
        existing_dept = db.query(Department).filter(
            func.lower(Department.name) == dept_data.name.lower()
        ).first()

        if existing_dept:
            raise HTTPException(
                status_code=400,
                detail=f"Department '{dept_data.name}' already exists."
            )

        # Save exactly as entered
        db_dept = Department(
            name=dept_data.name.strip(),
            code=dept_data.code.strip() if dept_data.code else None,
            description=dept_data.description,
            is_active=dept_data.is_active if dept_data.is_active is not None else True,
            is_deleted=dept_data.is_deleted if dept_data.is_deleted is not None else False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_dept)
        db.commit()
        db.refresh(db_dept)

        return serialize_department(db_dept)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB Error (Create Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating department")

    except Exception as e:
        db.rollback()
        print(f"Unexpected Error (Create Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while creating department")

# -------- Get Departments with search and pagination --------
def get_departments(
    db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None
) -> Dict[str, Any]:
    try:
        query = db.query(Department).filter(
            Department.is_deleted == False
        )

        if search:
            query = query.filter(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%"),
                    Department.description.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        departments = query.order_by(Department.id.asc()).offset(skip).limit(limit).all()
        departments_data = [serialize_department(dept) for dept in departments]

        return {
            "departments": departments_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1,
        }
    except SQLAlchemyError as e:
        print(f"DB Error (Get Departments): {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching departments")
    except Exception as e:
        print(f"Unexpected Error (Get Departments): {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while fetching departments")

# -------- Get Department by ID --------
def get_department_by_id(db: Session, dept_id: int) -> Optional[Dict[str, Any]]:
    try:
        dept = (
            db.query(Department)
            .filter(
                Department.id == dept_id,
                Department.is_deleted == False
                
            )
            .first()
        )
        return serialize_department(dept)
    except SQLAlchemyError as e:
        print(f"DB Error (Get Department by ID): {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching department")
    except Exception as e:
        print(f"Unexpected Error (Get Department by ID): {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while fetching department")

# -------- Update Department --------
def update_department(
    db: Session, dept_id: int, dept_data: DepartmentUpdate, login_id: int
) -> Optional[Dict[str, Any]]:
    try:
        db_dept = (
            db.query(Department)
            .filter(Department.id == dept_id, Department.is_deleted == False)
            .first()
        )
        if not db_dept:
            return None

        update_data = dept_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dept, field, value)

        db_dept.updated_by = login_id
        db.commit()
        db.refresh(db_dept)
        return serialize_department(db_dept)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB Error (Update Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating department")
    except Exception as e:
        db.rollback()
        print(f"Unexpected Error (Update Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while updating department")

# -------- Soft Delete Department --------
def delete_department(db: Session, dept_id: int, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_dept = (
            db.query(Department)
            .filter(Department.id == dept_id, Department.is_deleted == False)
            .first()
        )
        if not db_dept:
            return None

        db_dept.is_deleted = True
        db_dept.updated_by = login_id
        db.commit()
        db.refresh(db_dept)
        return serialize_department(db_dept)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB Error (Delete Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while deleting department")
    except Exception as e:
        db.rollback()
        print(f"Unexpected Error (Delete Department): {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while deleting department")
