from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List, Optional

from app.models.user_management.role_permission import RolePermission
from app.models.user_management.role import Role
from app.models.user_management.module import Module
from app.models.user_management.menu import Menu
from app.models.user_management.permission import Permission
from app.schemas.user_management.role_permission import RolePermissionCreate, RolePermissionUpdate


# =====================================================
# Serializer
# =====================================================
def serialize_role_permission(rp: RolePermission, db: Session) -> dict:
    """Convert RolePermission object into dictionary with related names."""
    permission_names = []
    if rp.permission_ids:
        try:
            ids = [int(pid) for pid in rp.permission_ids.split(",") if pid.strip().isdigit()]
            if ids:
                permission_names = [
                    p.name for p in db.query(Permission).filter(Permission.id.in_(ids)).all()
                ]
        except Exception:
            permission_names = []

    return {
        "id": rp.id,
        "role_id": rp.role_id,
        "role_name": rp.role.name if rp.role else None,
        "module_id": rp.module_id,
        "module_name": rp.module.name if rp.module else None,
        "menu_id": rp.menu_id,
        "menu_name": rp.menu.name if rp.menu else None,
        "permission_ids": rp.permission_ids,
        "permission_names": permission_names,
        "is_active": rp.is_active,
        "is_deleted": rp.is_deleted,
        "created_by": rp.created_by,
        "updated_by": rp.updated_by,
        "created_at": rp.created_at,
        "updated_at": rp.updated_at,
        "created_by_name": rp.created_user.full_name if rp.created_user else None,
        "updated_by_name": rp.updated_user.full_name if rp.updated_user else None,
    }


# =====================================================
# Bulk Create / Update
# =====================================================
def create_or_update_multiple_role_permissions(
    db: Session, rp_list: List[RolePermissionCreate], login_id: int
):
    """Bulk create or update role permissions."""
    result_list = []

    try:
        for rp_data in rp_list:
            db_rp = db.query(RolePermission).filter(
                RolePermission.role_id == rp_data.role_id,
                RolePermission.module_id == rp_data.module_id,
                RolePermission.menu_id == rp_data.menu_id,
                RolePermission.is_deleted == False,
            ).first()

            if db_rp:
                # Update existing record
                db_rp.permission_ids = rp_data.permission_ids
                db_rp.is_active = rp_data.is_active
                db_rp.updated_by = login_id
            else:
                # Create new record
                db_rp = RolePermission(
                    role_id=rp_data.role_id,
                    module_id=rp_data.module_id,
                    menu_id=rp_data.menu_id,
                    permission_ids=rp_data.permission_ids,
                    is_active=rp_data.is_active,
                    is_deleted=False,
                    created_by=login_id,
                )
                db.add(db_rp)

            db.flush()  # flush before refresh
            db.refresh(db_rp)
            result_list.append(serialize_role_permission(db_rp, db))

        db.commit()
        return result_list

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error during bulk create/update: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during bulk create/update: {str(e)}"
        )


# =====================================================
# Get All Neseted
# =====================================================


def get_nested_role_permissions(db: Session, skip: int = 0, limit: int = 10) -> dict:
    """
    Fetch role permissions in nested structure:
    Role -> Modules -> Menus -> Permissions
    """

    # Fetch all non-deleted role permissions
    rps = db.query(RolePermission).filter(RolePermission.is_deleted == False).all()

    roles_dict: Dict[str, Dict[str, List[Dict]]] = {}

    for rp in rps:
        role_name = rp.role.name
        module_name = rp.module.name
        menu_name = rp.menu.name

        # Fetch permission names
        permission_ids = [int(x) for x in rp.permission_ids.split(",") if x.strip().isdigit()]
        permissions = [p.name for p in db.query(Permission).filter(Permission.id.in_(permission_ids)).all()]

        # Build nested dict
        if role_name not in roles_dict:
            roles_dict[role_name] = {}
        if module_name not in roles_dict[role_name]:
            roles_dict[role_name][module_name] = []

        roles_dict[role_name][module_name].append({
            "rp_id": rp.id,
            "menu_name": menu_name,
            "menu_permissions": permissions
        })

    # Transform dict to list structure with aliases for schema
    roles_list = []
    for role, modules in roles_dict.items():
        modules_list = []
        for mod, menus in modules.items():
            modules_list.append({
                "module_name": mod,
                "module_menus": menus
            })
        roles_list.append({
            "role_name": role,
            "role_modules": modules_list
        })

    total = len(rps)

    return {
        "data_roles": roles_list,
        "total": total,
        "limit": limit,
        "page": (skip // limit) + 1
    }

def get_role_permissions(
    db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None
):
    """Fetch paginated list of role permissions with search support."""
    try:
        query = (
            db.query(RolePermission)
            .filter(RolePermission.is_deleted == False)
            .options(
                joinedload(RolePermission.role),
                joinedload(RolePermission.module),
                joinedload(RolePermission.menu),
            )
        )

        if search:
            query = (
                query.join(Role)
                .join(Module)
                .join(Menu)
                .filter(
                    or_(
                        Role.name.ilike(f"%{search}%"),
                        Module.name.ilike(f"%{search}%"),
                        Menu.name.ilike(f"%{search}%"),
                    )
                )
            )

        total = query.count()
        rps = query.offset(skip).limit(limit).all()
        rps_data = [serialize_role_permission(rp, db) for rp in rps]

        return {
            "role_permissions": rps_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1,
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching role permissions: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while fetching role permissions: {str(e)}"
        )


# =====================================================
# Get By ID
# =====================================================
def get_role_permission_by_id(db: Session, rp_id: int):
    """Fetch a single role permission by ID."""
    try:
        rp = (
            db.query(RolePermission)
            .filter(RolePermission.id == rp_id, RolePermission.is_deleted == False)
            .options(
                joinedload(RolePermission.role),
                joinedload(RolePermission.module),
                joinedload(RolePermission.menu),
            )
            .first()
        )

        return serialize_role_permission(rp, db) if rp else None

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching role permission by ID: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while fetching role permission by ID: {str(e)}"
        )


# =====================================================
# Update
# =====================================================
def update_role_permission(
    db: Session, rp_id: int, rp_data: RolePermissionUpdate, login_id: Optional[int] = None
):
    """Update role permission by ID."""
    try:
        db_rp = db.query(RolePermission).filter(
            RolePermission.id == rp_id,
            RolePermission.is_deleted == False,
        ).first()

        if not db_rp:
            return None

        update_data = rp_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rp, field, value)

        if login_id:
            db_rp.updated_by = login_id

        db.commit()
        db.refresh(db_rp)
        return serialize_role_permission(db_rp, db)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error while updating role permission: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while updating role permission: {str(e)}"
        )


# =====================================================
# Soft Delete
# =====================================================
def delete_role_permission(db: Session, rp_id: int, login_id: Optional[int] = None):
    """Soft delete role permission by ID."""
    try:
        db_rp = db.query(RolePermission).filter(
            RolePermission.id == rp_id,
            RolePermission.is_deleted == False,
        ).first()

        if not db_rp:
            return None

        db_rp.is_deleted = True
        if login_id:
            db_rp.updated_by = login_id

        db.commit()
        db.refresh(db_rp)
        return serialize_role_permission(db_rp, db)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error while deleting role permission: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while deleting role permission: {str(e)}"
        )
