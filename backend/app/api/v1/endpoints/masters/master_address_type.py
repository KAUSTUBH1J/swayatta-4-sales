from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_address_type import MasterAddresssTypes
from app.schemas.masters import master_address_type as ATSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_address_type as ATService
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
    response_model=ATSchema.MasterAddressTypeResponse,
    dependencies=[check_permission(2, "/address_types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_master_address_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: ATSchema.MasterAddressTypeCreate,
    db: Session = Depends(get_db)
):
    try:
        result = ATService.create_address_type(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Address Type created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Address Type failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=ATSchema.MasterAddressTypeResponse,
    dependencies=[check_permission(2, "/address_types", "view")],
    status_code=status.HTTP_200_OK
)
def list_master_address_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = ATService.get_address_types(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Address Types fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Address Types failed", getattr(e, "status_code", 500))


# -------------- Import Address Types ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/address_types", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterAddresssTypes)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Address Types failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{at_id}",
    response_model=ATSchema.MasterAddressTypeResponse,
    dependencies=[check_permission(2, "/address_types", "view")],
    status_code=status.HTTP_200_OK
)
def get_master_address_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = ATService.get_address_type_by_id(db, at_id)
        if not result:
            return handle_exception(Exception("Address Type not found"), "Fetching Address Type by ID failed", 404)
        return Response(
            json_data=result,
            message="Address Type fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Address Type")


# ---------------- UPDATE ----------------
@router.put(
    "/{at_id}",
    response_model=ATSchema.MasterAddressTypeResponse,
    dependencies=[check_permission(2, "/address_types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_master_address_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    data: ATSchema.MasterAddressTypeUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = ATService.update_address_type(db, at_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Address Type not found"), "Updating Address Type failed", 404)
        return Response(
            json_data=updated,
            message="Address Type updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Address Type update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{at_id}",
    response_model=ATSchema.MasterAddressTypeResponse,
    dependencies=[check_permission(2, "/address_types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_master_address_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    at_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = ATService.delete_address_type(db, at_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Address Type not found"), "Deleting Address Type failed", 404)
        return Response(
            json_data=deleted,
            message="Address Type deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Address Type failed", getattr(e, "status_code", 500))
