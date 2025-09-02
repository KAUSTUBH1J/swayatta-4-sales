from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import user_permission as UserPermissionSchemas
from app.utils.responses import Response
from app.services.user_management import user_permission_service as UserPermissionService
from app.core.permissions import check_permission

router = APIRouter()

# ---------------- Helper ----------------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )

# ---------------- Bulk Create/Update UserPermissions ----------------
@router.post("/", response_model=UserPermissionSchemas.UserPermissionResponse,
             dependencies=[check_permission(1, "/user-permissions", "create")],
             status_code=status.HTTP_201_CREATED)
def create_or_update_user_permissions_bulk(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    user_permissions: UserPermissionSchemas.MultiUserPermissionCreate,
    db: Session = Depends(get_db)
): 
    try:
        login_id = current_user.id
        result = UserPermissionService.create_or_update_multiple_user_permissions(
            db, user_permissions.user_permissions, login_id
        )
        return Response(
            json_data=result,
            message="User Permissions created/updated successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "User Permissions creation/updation failed", getattr(e, "status_code", 400))

# ---------------- List UserPermissions ----------------
@router.get("/", response_model=UserPermissionSchemas.UserPermissionResponse,
            dependencies=[check_permission(1, "/user-permissions", "view")],
            status_code=status.HTTP_200_OK)
def list_user_permissions(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = UserPermissionService.get_user_permissions(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="User Permissions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching User Permissions", getattr(e, "status_code", 500))

# ---------------- Get UserPermission by ID ----------------
@router.get("/{user_permission_id}", response_model=UserPermissionSchemas.UserPermissionResponse,
            dependencies=[check_permission(1, "/user-permissions", "view")],
            status_code=status.HTTP_200_OK)
def fetch_user_permission(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    user_permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        user_permission = UserPermissionService.get_user_permission_by_id(db, user_permission_id)
        if not user_permission:
            return handle_exception(Exception("User Permission not found"), "Error fetching User Permission", 404)
        return Response(
            json_data=user_permission,
            message="User Permission fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching User Permission", getattr(e, "status_code", 500))

# ---------------- Update UserPermission ----------------
@router.put("/{user_permission_id}", response_model=UserPermissionSchemas.UserPermissionResponse,
            dependencies=[check_permission(1, "/user-permissions", "edit")],
            status_code=status.HTTP_200_OK)
def update_user_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    user_permission_id: int,
    user_permission: UserPermissionSchemas.UserPermissionUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_user_permission = UserPermissionService.update_user_permission(
            db, user_permission_id, user_permission, login_id=current_user.id
        )
        if not updated_user_permission:
            return handle_exception(Exception("User Permission not found"), "Error updating User Permission", 404)
        return Response(
            json_data=updated_user_permission,
            message="User Permission updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating User Permission", getattr(e, "status_code", 500))

# ---------------- Delete UserPermission ----------------
@router.delete("/{user_permission_id}", response_model=UserPermissionSchemas.UserPermissionResponse,
               dependencies=[check_permission(1, "/user-permissions", "delete")],
               status_code=status.HTTP_200_OK)
def delete_user_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    user_permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_user_permission = UserPermissionService.delete_user_permission(db, user_permission_id, login_id=current_user.id)
        if not deleted_user_permission:
            return handle_exception(Exception("User Permission not found"), "Error deleting User Permission", 404)
        return Response(
            json_data=deleted_user_permission,
            message="User Permission deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting User Permission", getattr(e, "status_code", 500))
