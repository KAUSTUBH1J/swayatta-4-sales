from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_partner_type import MasterPartnerTypes
from app.schemas.masters import partner_type as PTSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import partner_type as PTService
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
    response_model=PTSchema.PartnerTypeResponse,
    dependencies=[check_permission(2, "/partner_types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_partner_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: PTSchema.PartnerTypeCreate,
    db: Session = Depends(get_db)
):
    try:
        result = PTService.create_partner_type(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Partner Type created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Partner Type failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=PTSchema.PartnerTypeResponse,
    dependencies=[check_permission(2, "/partner_types", "view")],
    status_code=status.HTTP_200_OK
)
def list_partner_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = PTService.get_partner_types(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Partner Types fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Partner Types failed", getattr(e, "status_code", 500))


# -------------- Import Partner Type ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/partner_types", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterPartnerTypes)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Partner Types failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{pt_id}",
    response_model=PTSchema.PartnerTypeResponse,
    dependencies=[check_permission(2, "/partner_types", "view")],
    status_code=status.HTTP_200_OK
)
def get_partner_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    pt_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = PTService.get_partner_type_by_id(db, pt_id)
        if not result:
            return handle_exception(Exception("Partner Type not found"), "Fetching Partner Type by ID failed", 404)
        return Response(
            json_data=result,
            message="Partner Type fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Partner Type")


# ---------------- UPDATE ----------------
@router.put(
    "/{pt_id}",
    response_model=PTSchema.PartnerTypeResponse,
    dependencies=[check_permission(2, "/partner_types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_partner_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    pt_id: int,
    data: PTSchema.PartnerTypeUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = PTService.update_partner_type(db, pt_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Partner Type not found"), "Updating Partner Type failed", 404)
        return Response(
            json_data=updated,
            message="Partner Type updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Partner Type update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{pt_id}",
    response_model=PTSchema.PartnerTypeResponse,
    dependencies=[check_permission(2, "/partner_types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_partner_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    pt_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = PTService.delete_partner_type(db, pt_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Partner Type not found"), "Deleting Partner Type failed", 404)
        return Response(
            json_data=deleted,
            message="Partner Type deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Partner Type failed", getattr(e, "status_code", 500))
