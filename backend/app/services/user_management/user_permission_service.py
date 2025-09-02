from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.models.user_management.user_permission import UserPermission
from app.models.user_management.user import User
from app.models.user_management.module import Module
from app.models.user_management.menu import Menu
from app.models.user_management.permission import Permission
from app.schemas.user_management.user_permission import UserPermissionCreate, UserPermissionUpdate

# ---------------- Serializer ----------------
def serialize_user_permission(up: UserPermission, db: Session) -> dict:
    permission_names = []
    if up.permission_ids:
        try:
            ids = [int(pid) for pid in up.permission_ids.split(",") if pid.strip().isdigit()]
            permission_names = [p.name for p in db.query(Permission).filter(Permission.id.in_(ids)).all()]
        except Exception:
            permission_names = []

    return {
        "id": up.id,
        "user_id": up.user_id,
        "user_name": up.user.full_name if up.user else None,
        "module_id": up.module_id,
        "module_name": up.module.name if up.module else None,
        "menu_id": up.menu_id,
        "menu_name": up.menu.name if up.menu else None,
        "permission_ids": up.permission_ids,
        "permission_names": permission_names,
        "is_active": up.is_active,
        "is_deleted": up.is_deleted,
        "created_by": up.created_by,
        "updated_by": up.updated_by,
        "created_at": up.created_at,
        "updated_at": up.updated_at,
        "created_by_name": up.created_user.full_name if up.created_user else None,
        "updated_by_name": up.updated_user.full_name if up.updated_user else None
    }

# ---------------- Bulk Create/Update ----------------
def create_or_update_multiple_user_permissions(db: Session, up_list: List[UserPermissionCreate], login_id: int):
    result_list = []

    try:
        for up_data in up_list:
            db_up = db.query(UserPermission).filter(
                UserPermission.user_id == up_data.user_id,
                UserPermission.module_id == up_data.module_id,
                UserPermission.menu_id == up_data.menu_id,
                UserPermission.is_deleted == False
            ).first()

            if db_up:
                db_up.permission_ids = up_data.permission_ids
                db_up.is_active = up_data.is_active
                db_up.updated_by = login_id
            else:
                db_up = UserPermission(
                    user_id=up_data.user_id,
                    module_id=up_data.module_id,
                    menu_id=up_data.menu_id,
                    permission_ids=up_data.permission_ids,
                    is_active=up_data.is_active,
                    is_deleted=False,
                    created_by=login_id
                )
                db.add(db_up)

            db.commit()
            db.refresh(db_up)
            result_list.append(serialize_user_permission(db_up, db))

        return result_list

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during bulk create/update: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error during bulk create/update: {str(e)}")

# ---------------- Get All ----------------
def get_user_permissions(db: Session, skip: int = 0, limit: int = 50, search: str = None):
    try:
        query = db.query(UserPermission).filter(UserPermission.is_deleted == False)\
            .options(joinedload(UserPermission.user),
                     joinedload(UserPermission.module),
                     joinedload(UserPermission.menu))

        if search:
            query = query.join(User).join(Module).join(Menu).filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    Module.name.ilike(f"%{search}%"),
                    Menu.name.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        ups = query.offset(skip).limit(limit).all()
        ups_data = [serialize_user_permission(up, db) for up in ups]

        return {
            "user_permissions": ups_data,
            "total": total,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching user permissions: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching user permissions: {str(e)}")

# ---------------- Get By ID ----------------
def get_user_permission_by_id(db: Session, up_id: int):
    try:
        up = db.query(UserPermission).filter(
            UserPermission.id == up_id,
            UserPermission.is_deleted == False
        ).options(
            joinedload(UserPermission.user),
            joinedload(UserPermission.module),
            joinedload(UserPermission.menu)
        ).first()

        return serialize_user_permission(up, db) if up else None

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching user permission by ID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching user permission by ID: {str(e)}")

# ---------------- Update ----------------
def update_user_permission(db: Session, up_id: int, up_data: UserPermissionUpdate, login_id: int = None):
    try:
        db_up = db.query(UserPermission).filter(
            UserPermission.id == up_id, UserPermission.is_deleted == False
        ).first()

        if not db_up:
            return None

        update_data = up_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_up, field, value)

        if login_id:
            db_up.updated_by = login_id

        db.commit()
        db.refresh(db_up)
        return serialize_user_permission(db_up, db)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while updating user permission: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error while updating user permission: {str(e)}")

# ---------------- Soft Delete ----------------
def delete_user_permission(db: Session, up_id: int, login_id: int = None):
    try:
        db_up = db.query(UserPermission).filter(
            UserPermission.id == up_id, UserPermission.is_deleted == False
        ).first()

        if not db_up:
            return None

        db_up.is_deleted = True
        if login_id:
            db_up.updated_by = login_id

        db.commit()
        db.refresh(db_up)
        return serialize_user_permission(db_up, db)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while deleting user permission: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error while deleting user permission: {str(e)}")
