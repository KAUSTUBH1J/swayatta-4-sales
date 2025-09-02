from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_countries import MasterCountries
from app.schemas.masters import master_countries as CountrySchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_countries as CountryService
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
    response_model=CountrySchema.MasterCountryResponse,
    dependencies=[check_permission(2, "/countries", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_country(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: CountrySchema.MasterCountryCreate,
    db: Session = Depends(get_db)
):
    try:
        result = CountryService.create_country(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Country created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Country failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=CountrySchema.MasterCountryResponse,
    dependencies=[check_permission(2, "/countries", "view")],
    status_code=status.HTTP_200_OK
)
def list_countries(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = CountryService.get_countries(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Countries fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Countries failed", getattr(e, "status_code", 500))


# -------------- Import Countries ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/countries", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterCountries)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Countries failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{country_id}",
    response_model=CountrySchema.MasterCountryResponse,
    dependencies=[check_permission(2, "/countries", "view")],
    status_code=status.HTTP_200_OK
)
def get_country(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    country_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = CountryService.get_country_by_id(db, country_id)
        if not result:
            return handle_exception(Exception("Country not found"), "Fetching Country by ID failed", 404)
        return Response(
            json_data=result,
            message="Country fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Country")


# ---------------- UPDATE ----------------
@router.put(
    "/{country_id}",
    response_model=CountrySchema.MasterCountryResponse,
    dependencies=[check_permission(2, "/countries", "edit")],
    status_code=status.HTTP_200_OK
)
def update_country(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    country_id: int,
    data: CountrySchema.MasterCountryUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = CountryService.update_country(db, country_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Country not found"), "Updating Country failed", 404)
        return Response(
            json_data=updated,
            message="Country updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Country update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{country_id}",
    response_model=CountrySchema.MasterCountryResponse,
    dependencies=[check_permission(2, "/countries", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_country(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    country_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = CountryService.delete_country(db, country_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Country not found"), "Deleting Country failed", 404)
        return Response(
            json_data=deleted,
            message="Country deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Country failed", getattr(e, "status_code", 500))
