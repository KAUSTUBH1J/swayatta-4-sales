from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import or_
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from fastapi import FastAPI,status
from app.models.user_management.permission import Permission
from app.schemas.user_management.permission import PermissionCreate, PermissionUpdate

# ---------------- Serializer ----------------
def serialize_permission(permission: Permission) -> Dict[str, Any]:
    return {
        "id": permission.id,
        "name": permission.name,
        "description": permission.description,
        "is_active": permission.is_active,
        "is_deleted": permission.is_deleted,
        "created_by": permission.created_by,
        "updated_by": permission.updated_by,
        "created_at": permission.created_at,
        "updated_at": permission.updated_at,
        "created_by_name": permission.created_user.full_name if permission.created_user else None,
        "updated_by_name": permission.updated_user.full_name if permission.updated_user else None
    }

# ---------------- Create ----------------
def create_permission(db: Session, data: PermissionCreate, login_id: int) -> Dict[str, Any]:
    try:
        # Duplicate check (case-insensitive, only non-deleted)
        existing_permission = db.query(Permission).filter(
            func.lower(Permission.name) == data.name.lower(),
            Permission.is_deleted == False
        ).first()

        if existing_permission:
            raise HTTPException(
                status_code=400,
                detail=f"Permission '{data.name}' already exists."
            )

        # Save exactly as entered
        db_permission = Permission(
            name=data.name.strip(),
            description=data.description,
            is_active=data.is_active,
            is_deleted=False,
            created_by=login_id,
            updated_by=login_id
        )

        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)

        return serialize_permission(db_permission)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create Permission):", str(e))
        raise HTTPException(status_code=500, detail="Database error occurred while creating permission")

    except Exception as e:
        db.rollback()
        print("Unexpected Error (Create Permission):", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong while creating permission")

# ---------------- Get All (with search + pagination) ----------------
def get_permissions(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
    try:
        query = db.query(Permission).filter(Permission.is_deleted == False)

        if search:
            query = query.filter(
                or_(
                    Permission.name.ilike(f"%{search}%"),
                    Permission.description.ilike(f"%{search}%")
                )
            )

        total = query.count()
        permissions = query.order_by(Permission.id.asc()).offset(skip).limit(limit).all()
        return {
            "permissions": [serialize_permission(p) for p in permissions],
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching permissions: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching permissions: {str(e)}")

# ---------------- Get by ID ----------------
def get_permission_by_id(db: Session, permission_id: int) -> Optional[Dict[str, Any]]:
    try:
        permission = db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False,
            Permission.is_active == True
        ).first()
        return serialize_permission(permission) if permission else None

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching permission: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching permission: {str(e)}")

# ---------------- Update ----------------
def update_permission(db: Session, permission_id: int, data: PermissionUpdate, login_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    try:
        db_permission = db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()

        if not db_permission:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_permission, field, value)

        if login_id:
            db_permission.updated_by = login_id

        db.commit()
        db.refresh(db_permission)
        return serialize_permission(db_permission)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while updating permission: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error while updating permission: {str(e)}")

# ---------------- Soft Delete ----------------
def delete_permission(db: Session, permission_id: int, login_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    try:
        db_permission = db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()

        if not db_permission:
            return None

        db_permission.is_deleted = True
        if login_id:
            db_permission.updated_by = login_id

        db.commit()
        db.refresh(db_permission)
        return serialize_permission(db_permission)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while deleting permission: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error while deleting permission: {str(e)}")
