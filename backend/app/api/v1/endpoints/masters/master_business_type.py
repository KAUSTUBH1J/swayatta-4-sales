from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_business_types import MasterBusinessTypes
from app.schemas.masters import master_business_type as BTSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_business_type as BTService
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
    response_model=BTSchema.MasterBusinessTypeResponse,
    dependencies=[check_permission(2, "/business_types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_business_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: BTSchema.MasterBusinessTypeCreate,
    db: Session = Depends(get_db)
):
    try:
        result = BTService.create_business_type(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Business Type created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Business Type failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=BTSchema.MasterBusinessTypeResponse,
    dependencies=[check_permission(2, "/business_types", "view")],
    status_code=status.HTTP_200_OK
)
def list_business_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = BTService.get_business_types(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Business Types fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Business Types failed", getattr(e, "status_code", 500))


# -------------- Import Business Types ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/business_types", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterBusinessTypes)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Business Types failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{bt_id}",
    response_model=BTSchema.MasterBusinessTypeResponse,
    dependencies=[check_permission(2, "/business_types", "view")],
    status_code=status.HTTP_200_OK
)
def get_business_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bt_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = BTService.get_business_type_by_id(db, bt_id)
        if not result:
            return handle_exception(Exception("Business Type not found"), "Fetching Business Type by ID failed", 404)
        return Response(
            json_data=result,
            message="Business Type fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Business Type")


# ---------------- UPDATE ----------------
@router.put(
    "/{bt_id}",
    response_model=BTSchema.MasterBusinessTypeResponse,
    dependencies=[check_permission(2, "/business_types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_business_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bt_id: int,
    data: BTSchema.MasterBusinessTypeUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = BTService.update_business_type(db, bt_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Business Type not found"), "Updating Business Type failed", 404)
        return Response(
            json_data=updated,
            message="Business Type updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Business Type update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{bt_id}",
    response_model=BTSchema.MasterBusinessTypeResponse,
    dependencies=[check_permission(2, "/business_types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_business_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bt_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = BTService.delete_business_type(db, bt_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Business Type not found"), "Deleting Business Type failed", 404)
        return Response(
            json_data=deleted,
            message="Business Type deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Business Type failed", getattr(e, "status_code", 500))
