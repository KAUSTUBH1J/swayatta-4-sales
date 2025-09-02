from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user_management.user import User
from app.models.user_management.menu import Menu
from app.models.user_management.permission import Permission
from app.models.user_management.role_permission import RolePermission
from app.models.user_management.user_permission import UserPermission
from app.core.auth_service import get_current_user


def check_permission(module_id: int, path: str, permission_name: str):
    """
    Checks if current user has required permission based on:
    1. Assigned module
    2. Role-based permission (CSV)
    3. User-specific permission (CSV override)
    """
    def wrapper(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # --- Step 1: Check Module Access ---
        if not current_user.assign_modules:
            raise HTTPException(status_code=403, detail="No modules assigned to user")

        assigned_module_ids = [int(m.strip()) for m in current_user.assign_modules.split(",") if m.strip()]
        if module_id not in assigned_module_ids:
            raise HTTPException(status_code=403, detail="Access to module denied")

        # --- Step 2: Identify Menu for Path ---
        menu = db.query(Menu).filter(
            Menu.module_id == module_id,
            Menu.path == path,
            Menu.is_active == True,
            Menu.is_deleted == False
        ).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found for given path")

        # --- Step 3: Identify Permission ID ---
        permission = db.query(Permission).filter(
            Permission.name == permission_name,
            Permission.is_active == True,
            Permission.is_deleted == False
        ).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission type not found")

        # --- Step 4: Check User-Specific Permission (CSV override) ---
        user_perm = db.query(UserPermission).filter(
            UserPermission.user_id == current_user.id,
            UserPermission.module_id == module_id,
            UserPermission.menu_id == menu.id,
            UserPermission.is_active == True,
            UserPermission.is_deleted == False
        ).first()

        if user_perm and user_perm.permission_ids:
            user_perm_ids = [int(pid.strip()) for pid in user_perm.permission_ids.split(",") if pid.strip()]
            if permission.id in user_perm_ids:
                return  #User override allow

        # --- Step 5: Check Role-Based Permission (CSV check) ---
        if not current_user.role_id:
            raise HTTPException(status_code=403, detail="No role assigned to user")

        role_perm = db.query(RolePermission).filter(
            RolePermission.role_id == current_user.role_id,
            RolePermission.module_id == module_id,
            RolePermission.menu_id == menu.id,
            RolePermission.is_active == True,
            RolePermission.is_deleted == False
        ).first()

        if not role_perm or not role_perm.permission_ids:
            raise HTTPException(status_code=403, detail="Permission denied by role")

        role_perm_ids = [int(pid.strip()) for pid in role_perm.permission_ids.split(",") if pid.strip()]
        if permission.id not in role_perm_ids:
            raise HTTPException(status_code=403, detail="Permission denied by role")

        return  #Access granted

    return Depends(wrapper)


