from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import role_permission as RolePermissionSchemas
from app.utils.responses import Response
from app.services.user_management import role_permission_service as RolePermissionService
from app.core.permissions import check_permission

router = APIRouter()

# ---------------- Helper ----------------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )

# ---------------- Bulk Create/Update RolePermissions ----------------
@router.post("/", response_model=RolePermissionSchemas.RolePermissionResponse,
             dependencies=[check_permission(1, "/role-permissions", "create")],
             status_code=status.HTTP_201_CREATED)
def create_or_update_role_permissions_bulk(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    role_permissions: RolePermissionSchemas.MultiRolePermissionCreate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        result = RolePermissionService.create_or_update_multiple_role_permissions(
            db, role_permissions.role_permissions, login_id
        )
        return Response(
            json_data=result,
            message="Role Permissions created/updated successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Role Permissions creation/updation failed", getattr(e, "status_code", 400))

# ---------------- List RolePermissions ----------------
@router.get("/", response_model=RolePermissionSchemas.RolePermissionResponse,
            dependencies=[check_permission(1, "/role-permissions", "view")],
            status_code=status.HTTP_200_OK)
def list_role_permissions(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = RolePermissionService.get_role_permissions(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Role Permissions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching Role Permissions", getattr(e, "status_code", 500))


# ---------------- List Nested RolePermissions ----------------
@router.get(
    "/role-permissions/nested",
    response_model=RolePermissionSchemas.NestedRolePermissionResponse,
    dependencies=[check_permission(1, "/role-permissions", "view")],
    status_code=status.HTTP_200_OK
)
def list_nested_role_permissions(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    try:
        offset = (page - 1) * limit
        result = RolePermissionService.get_nested_role_permissions(db, skip=offset, limit=limit)
        return Response(
            json_data=result,
            message="Nested Role Permissions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(
            e,
            "Error fetching Nested Role Permissions",
            getattr(e, "status_code", 500)
        )


# ---------------- Get RolePermission by ID ----------------
@router.get("/{role_permission_id}", response_model=RolePermissionSchemas.RolePermissionResponse,
            dependencies=[check_permission(1, "/role-permissions", "view")],
            status_code=status.HTTP_200_OK)
def fetch_role_permission(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    role_permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        role_permission = RolePermissionService.get_role_permission_by_id(db, role_permission_id)
        if not role_permission:
            return handle_exception(Exception("Role Permission not found"), "Error fetching Role Permission", 404)
        return Response(
            json_data=role_permission,
            message="Role Permission fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching Role Permission", getattr(e, "status_code", 500))

# ---------------- Update RolePermission ----------------
@router.put("/{role_permission_id}", response_model=RolePermissionSchemas.RolePermissionResponse,
            dependencies=[check_permission(1, "/role-permissions", "edit")],
            status_code=status.HTTP_200_OK)
def update_role_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    role_permission_id: int,
    role_permission: RolePermissionSchemas.RolePermissionUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_role_permission = RolePermissionService.update_role_permission(
            db, role_permission_id, role_permission, login_id=current_user.id
        )
        if not updated_role_permission:
            return handle_exception(Exception("Role Permission not found"), "Error updating Role Permission", 404)
        return Response(
            json_data=updated_role_permission,
            message="Role Permission updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating Role Permission", getattr(e, "status_code", 500))

# ---------------- Delete RolePermission ----------------
@router.delete("/{role_permission_id}", response_model=RolePermissionSchemas.RolePermissionResponse,
               dependencies=[check_permission(1, "/role-permissions", "delete")],
               status_code=status.HTTP_200_OK)
def delete_role_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    role_permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_role_permission = RolePermissionService.delete_role_permission(db, role_permission_id, login_id=current_user.id)
        if not deleted_role_permission:
            return handle_exception(Exception("Role Permission not found"), "Error deleting Role Permission", 404)
        return Response(
            json_data=deleted_role_permission,
            message="Role Permission deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting Role Permission", getattr(e, "status_code", 500))
