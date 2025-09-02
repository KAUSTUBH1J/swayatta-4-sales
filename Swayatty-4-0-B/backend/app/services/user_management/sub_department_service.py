from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.models.user_management.sub_department import SubDepartment
from app.schemas.user_management.sub_department import SubDepartmentCreate, SubDepartmentUpdate

# ---------------- Serializer ----------------
def serialize_sub_department(sub_dept: SubDepartment) -> Optional[Dict[str, Any]]:
    if not sub_dept:
        return None
    return {
        "id": sub_dept.id,
        "name": sub_dept.name,
        "code": sub_dept.code,
        "department_id": sub_dept.department_id,
        "department_name": sub_dept.department.name if sub_dept.department else None,
        "description": sub_dept.description,
        "is_active": sub_dept.is_active,
        "is_deleted": sub_dept.is_deleted,
        "created_by": sub_dept.created_by,
        "updated_by": sub_dept.updated_by,
        "created_at": sub_dept.created_at,
        "updated_at": sub_dept.updated_at,
        "created_by_name": sub_dept.created_user.full_name if sub_dept.created_user else None,
        "updated_by_name": sub_dept.updated_user.full_name if sub_dept.updated_user else None,
    }

# ---------------- Create with Duplicate Check ----------------
def create_sub_department(db: Session, sub_dept_data: SubDepartmentCreate, login_id: int) -> Dict[str, Any]:
    try:
        # ===== Duplicate Name Check =====
        existing_sub_dept = db.query(SubDepartment).filter(
            func.lower(SubDepartment.name) == sub_dept_data.name.lower(),
            SubDepartment.department_id == sub_dept_data.department_id,
            SubDepartment.is_deleted == False
        ).first()
        if existing_sub_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SubDepartment '{sub_dept_data.name}' already exists in this department."
            )

        db_sub_dept = SubDepartment(
            name=sub_dept_data.name,
            code=sub_dept_data.code,
            department_id=sub_dept_data.department_id,
            description=sub_dept_data.description,
            is_active=sub_dept_data.is_active if sub_dept_data.is_active is not None else True,
            is_deleted=False,
            created_by=login_id
        )
        db.add(db_sub_dept)
        db.commit()
        db.refresh(db_sub_dept)
        return serialize_sub_department(db_sub_dept)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create SubDepartment):", str(e))
        raise HTTPException(status_code=500, detail="Database error while creating sub department")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating sub department: {str(e)}")

# ---------------- Get All ----------------
def get_sub_departments(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> dict:
    try:
        query = db.query(SubDepartment).filter(
            SubDepartment.is_deleted == False
        )
        if search:
            query = query.filter(
                or_(
                    SubDepartment.name.ilike(f"%{search}%"),
                    SubDepartment.code.ilike(f"%{search}%"),
                    SubDepartment.description.ilike(f"%{search}%")
                )
            )
        total = query.count()
        sub_departments = query.order_by(SubDepartment.id.asc()).offset(skip).limit(limit).all()
        return {
            "sub_departments": [serialize_sub_department(sd) for sd in sub_departments],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Get SubDepartments):", str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching sub departments")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sub departments: {str(e)}")

# ---------------- Get by ID ----------------
def get_sub_department_by_id(db: Session, sub_dept_id: int) -> Optional[Dict[str, Any]]:
    try:
        sub_dept = db.query(SubDepartment).filter(
            SubDepartment.id == sub_dept_id,
            SubDepartment.is_deleted == False
        ).first()
        return serialize_sub_department(sub_dept)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while fetching sub department by ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sub department by ID: {str(e)}")

# ---------------- Update with Duplicate Check ----------------
def update_sub_department(db: Session, sub_dept_id: int, sub_dept_data: SubDepartmentUpdate, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_sub_dept = db.query(SubDepartment).filter(SubDepartment.id == sub_dept_id, SubDepartment.is_deleted == False).first()
        if not db_sub_dept:
            return None

        update_data = sub_dept_data.dict(exclude_unset=True)

        # Duplicate name check
        if "name" in update_data:
            existing_sub_dept = db.query(SubDepartment).filter(
                func.lower(SubDepartment.name) == update_data["name"].lower(),
                SubDepartment.department_id == (update_data.get("department_id", db_sub_dept.department_id)),
                SubDepartment.id != sub_dept_id,
                SubDepartment.is_deleted == False
            ).first()
            if existing_sub_dept:
                raise HTTPException(status_code=400, detail=f"SubDepartment '{update_data['name']}' already exists in this department.")

        for field, value in update_data.items():
            setattr(db_sub_dept, field, value)

        db_sub_dept.updated_by = login_id
        db.commit()
        db.refresh(db_sub_dept)
        return serialize_sub_department(db_sub_dept)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating sub department")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating sub department: {str(e)}")

# ---------------- Soft Delete ----------------
def delete_sub_department(db: Session, sub_dept_id: int, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_sub_dept = db.query(SubDepartment).filter(SubDepartment.id == sub_dept_id, SubDepartment.is_deleted == False).first()
        if not db_sub_dept:
            return None
        db_sub_dept.is_deleted = True
        db_sub_dept.updated_by = login_id
        db.commit()
        db.refresh(db_sub_dept)
        return serialize_sub_department(db_sub_dept)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting sub department")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting sub department: {str(e)}")
