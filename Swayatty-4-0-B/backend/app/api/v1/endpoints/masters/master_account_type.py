from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_account_types import MasterAccountTypes
from app.schemas.masters import master_account_types as ATSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_account_type as ATService
from app.utils.Import_helper.common_import_file import import_csv_to_model

router = APIRouter()

# Helper for consistent error handling
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=ATSchema.MasterAccountTypeResponse,
    dependencies=[check_permission(2, "/account_types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_account_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: ATSchema.MasterAccountTypeCreate,
    db: Session = Depends(get_db)
):
    try:
        result = ATService.create_account_type(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Account Type created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Account Type failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=ATSchema.MasterAccountTypeResponse,
    dependencies=[check_permission(2, "/account_types", "view")],
    status_code=status.HTTP_200_OK
)
def list_account_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = ATService.get_account_types(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Account Types fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Account Types failed", getattr(e, "status_code", 500))


# -------------- Import Account Type ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/account_types", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterAccountTypes)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Account Types failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{at_id}",
    response_model=ATSchema.MasterAccountTypeResponse,
    dependencies=[check_permission(2, "/account_types", "view")],
    status_code=status.HTTP_200_OK
)
def get_account_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = ATService.get_account_type_by_id(db, at_id)
        if not result:
            return handle_exception(Exception("Account Type not found"), "Fetching Account Type by ID failed", 404)
        return Response(
            json_data=result,
            message="Account Type fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Account Type")


# ---------------- UPDATE ----------------
@router.put(
    "/{at_id}",
    response_model=ATSchema.MasterAccountTypeResponse,
    dependencies=[check_permission(2, "/account_types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_account_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    data: ATSchema.MasterAccountTypeUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = ATService.update_account_type(db, at_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Account Type not found"), "Updating Account Type failed", 404)
        return Response(
            json_data=updated,
            message="Account Type updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Account Type update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{at_id}",
    response_model=ATSchema.MasterAccountTypeResponse,
    dependencies=[check_permission(2, "/account_types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_account_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = ATService.delete_account_type(db, at_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Account Type not found"), "Deleting Account Type failed", 404)
        return Response(
            json_data=deleted,
            message="Account Type deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Account Type failed", getattr(e, "status_code", 500))
