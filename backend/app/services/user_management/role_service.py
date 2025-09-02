from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy import or_, func

from app.models.user_management.role import Role
from app.schemas.user_management.role import RoleCreate, RoleUpdate

# ---------------- Map Role ----------------
def map_role_with_names(role: Role) -> Optional[Dict[str, Any]]:
    if not role:
        return None
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "is_deleted": role.is_deleted,
        "created_by": role.created_by,
        "updated_by": role.updated_by,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "created_by_name": role.created_user.full_name if role.created_user else None,
        "updated_by_name": role.updated_user.full_name if role.updated_user else None
    }

# ---------------- Create Role with Duplicate Check ----------------
def create_role(db: Session, role_data: RoleCreate, login_id: int) -> Dict[str, Any]:
    try:
        # ===== Duplicate Name Check =====
        existing_role = db.query(Role).filter(
            func.lower(Role.name) == role_data.name.lower(),
            Role.is_deleted == False
        ).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role name '{role_data.name}' already exists."
            )

        # ===== Create Role =====
        db_role = Role(
            name=role_data.name,
            description=role_data.description,
            is_active=role_data.is_active if role_data.is_active is not None else True,
            is_deleted=False,
            created_by=login_id
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return map_role_with_names(db_role)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print("DB Error (Create Role):", str(e))
        raise HTTPException(status_code=500, detail="Database error while creating role")
    except Exception as e:
        db.rollback()
        print("Unexpected Error (Create Role):", str(e))
        raise HTTPException(status_code=500, detail=f"Error creating role: {str(e)}")

# ---------------- Get All Roles ----------------
def get_roles(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
    try:
        # query = db.query(Role).filter(Role.is_deleted == False)
        query = db.query(Role).filter(Role.is_deleted.is_(False))

        if search:
            query = query.filter(
                or_(
                    Role.name.ilike(f"%{search}%"),
                    Role.description.ilike(f"%{search}%")
                )
            )
        total = query.count()
        roles = query.order_by(Role.id.asc()).offset(skip).limit(limit).all()
        roles_data = [map_role_with_names(r) for r in roles]
        return {"roles": roles_data, "total": total, "limit": limit, "page": (skip // limit) + 1}
    except SQLAlchemyError as e:
        print("DB Error (Get Roles):", str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching roles")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roles: {str(e)}")

# ---------------- Get Role by ID ----------------
def get_role_by_id(db: Session, role_id: int) -> Optional[Dict[str, Any]]:
    try:
        role = db.query(Role).filter(
            Role.id == role_id,
            Role.is_deleted == False
        ).first()
        return map_role_with_names(role)
    except SQLAlchemyError as e:
        print("DB Error (Get Role by ID):", str(e))
        raise HTTPException(status_code=500, detail="Database error while fetching role by ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching role by ID: {str(e)}")

# ---------------- Update Role with Duplicate Check ----------------
def update_role(db: Session, role_id: int, role_data: RoleUpdate, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
        if not db_role:
            return None

        update_data = role_data.dict(exclude_unset=True)

        # Duplicate name check
        if "name" in update_data:
            existing_role = db.query(Role).filter(
                func.lower(Role.name) == update_data["name"].lower(),
                Role.id != role_id,
                Role.is_deleted == False
            ).first()
            if existing_role:
                raise HTTPException(status_code=400, detail=f"Role name '{update_data['name']}' already exists.")

        for field, value in update_data.items():
            setattr(db_role, field, value)
        db_role.updated_by = login_id
        db.commit()
        db.refresh(db_role)
        return map_role_with_names(db_role)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating role")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")

# ---------------- Soft Delete Role ----------------
def delete_role(db: Session, role_id: int, login_id: int) -> Optional[Dict[str, Any]]:
    try:
        db_role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
        if not db_role:
            return None
        db_role.is_deleted = True
        db_role.updated_by = login_id
        db.commit()
        db.refresh(db_role)
        return map_role_with_names(db_role)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting role")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")
