from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.schemas.user_management import role as RoleSchemas
from app.schemas.user_management import user as UserSchemas
from app.services.user_management import role_service as RoleService
from app.utils.export_helper.common_export_file import transform_roles_for_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.models.user_management.role import Role
from app.schemas.user_management.role import RoleExportOut
from app.utils.Import_helper.common_import_file import import_csv_to_model

router = APIRouter()

# Helper for consistent error handling
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )

# ---------------- CREATE ROLE ----------------
@router.post(
    "/", 
    response_model=RoleSchemas.RoleResponse, 
    dependencies=[check_permission(1, "/roles", "create")], 
    status_code=status.HTTP_201_CREATED
)
def create_role(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    role: RoleSchemas.RoleCreate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        result = RoleService.create_role(db, role, login_id)
        return Response(
            json_data=result, 
            message="Role created successfully", 
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating role failed", getattr(e, "status_code", 500))

# ---------------- LIST ROLES ----------------
@router.get(
    "/", 
    response_model=RoleSchemas.RoleResponse, 
    dependencies=[check_permission(1, "/roles", "view")],
    status_code=status.HTTP_200_OK
)
def list_roles(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
): 
    try:
        offset = (page - 1) * limit
        result = RoleService.get_roles(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result, 
            message="Roles fetched successfully", 
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching roles failed", getattr(e, "status_code", 500))


# ----------------- Export Role ----------------------------
@router.get(
    "/export",
    response_model=RoleSchemas.RoleExportOut,
    dependencies=[check_permission(1, "/roles", "export")],
    status_code=status.HTTP_200_OK
)
def export_roles(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        roles = db.query(Role).all()
        role_schema_list = transform_roles_for_export(roles)
        return export_to_csv(role_schema_list, RoleExportOut, filename="roles.csv")
    except Exception as e:
        return handle_exception(e, "Exporting roles failed", getattr(e, "status_code", 500))


# -------------- Import Role ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/roles", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, Role)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing roles failed", getattr(e, "status_code", 500))



# ---------------- GET ROLE BY ID ----------------
@router.get(
    "/{role_id}", 
    response_model=RoleSchemas.RoleResponse,
    dependencies=[check_permission(1, "/roles", "view")],
    status_code=status.HTTP_200_OK
)
def get_role(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    role_id: int,
    db: Session = Depends(get_db)
):
    try:
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            return handle_exception(Exception("Role not found"), "Fetching role by ID failed", 404)
        return Response(
            json_data=role, 
            message="Role fetched successfully", 
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching role by ID failed", getattr(e, "status_code", 500))



# ---------------- UPDATE ROLE ----------------
@router.put(
    "/{role_id}",
    response_model=RoleSchemas.RoleResponse,
    dependencies=[check_permission(1, "/roles", "edit")],
    status_code=status.HTTP_200_OK
)
def update_role(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    role_id: int,
    role: RoleSchemas.RoleUpdate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        updated_role = RoleService.update_role(db, role_id, role, login_id)
        if not updated_role:
            return handle_exception(Exception("Role not found"), "Updating role failed", 404)
        return Response(
            json_data=updated_role,
            message="Role updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating role failed", getattr(e, "status_code", 500))


# ---------------- DELETE ROLE (Soft Delete) ----------------
@router.delete(
    "/{role_id}",
    response_model=RoleSchemas.RoleResponse,
    dependencies=[check_permission(1, "/roles", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_role(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    role_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_role = RoleService.delete_role(db, role_id, current_user.id)
        if not deleted_role:
            return handle_exception(Exception("Role not found"), "Deleting role failed", 404)
        return Response(
            json_data=deleted_role,
            message="Role deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting role failed", getattr(e, "status_code", 500))


