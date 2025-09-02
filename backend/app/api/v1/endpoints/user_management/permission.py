from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import permission as PermissionSchemas
from app.utils.responses import Response
from app.services.user_management import permission_service as PermissionService
from app.core.permissions import check_permission

router = APIRouter()

# ---------------- Helper for consistent error handling ----------------

def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )


# ---------------- Create Permission ----------------
@router.post("/", response_model=PermissionSchemas.PermissionResponse,
             dependencies=[check_permission(1, "/permissions", "create")],
             status_code=status.HTTP_201_CREATED)
def create_permission(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    permission: PermissionSchemas.PermissionCreate,
    db: Session = Depends(get_db)
):
    try:
        result = PermissionService.create_permission(db, permission, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Permission created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Permission failed", getattr(e, "status_code", 500))


# ---------------- List Permissions ----------------
@router.get("/", response_model=PermissionSchemas.PermissionResponse,
            dependencies=[check_permission(1, "/permissions", "view")],
            status_code=status.HTTP_200_OK)
def list_permissions(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = PermissionService.get_permissions(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Permissions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Permission failed", getattr(e, "status_code", 500))


# ---------------- Get Permission by ID ----------------
@router.get("/{permission_id}", response_model=PermissionSchemas.PermissionResponse,
            dependencies=[check_permission(1, "/permissions", "view")],
            status_code=status.HTTP_200_OK)
def fetch_permission(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        permission = PermissionService.get_permission_by_id(db, permission_id)
        if not permission:
            return handle_exception(Exception("Permission not found"), "Fetching Permission by ID failed" ,404)
        return Response(
            json_data=permission,
            message="Permission fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Permission by ID failed", getattr(e, "status_code", 500))


# ---------------- Update Permission ----------------
@router.put("/{permission_id}", response_model=PermissionSchemas.PermissionResponse,
            dependencies=[check_permission(1, "/permissions", "edit")],
            status_code=status.HTTP_200_OK)
def update_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    permission_id: int,
    permission: PermissionSchemas.PermissionUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = PermissionService.update_permission(db, permission_id, permission, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Permission not found"), "Fetching Permission by ID failed" ,404)
        return Response(
            json_data=updated,
            message="Permission updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating Permission failed", getattr(e, "status_code", 500))


# ---------------- Delete Permission ----------------
@router.delete("/{permission_id}", response_model=PermissionSchemas.PermissionResponse,
               dependencies=[check_permission(1, "/permissions", "delete")],
               status_code=status.HTTP_200_OK)
def delete_permission_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    permission_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = PermissionService.delete_permission(db, permission_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Permission not found"), "Fetching Permission by ID failed" ,404)
        return Response(
            json_data=deleted,
            message="Permission deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Permission failed", getattr(e, "status_code", 500))
