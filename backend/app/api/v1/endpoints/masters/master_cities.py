from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_cities import MasterCities
from app.schemas.masters import master_cities as CitySchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_cities as CityService
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
    response_model=CitySchema.MasterCityResponse,
    dependencies=[check_permission(2, "/cities", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_city(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: CitySchema.MasterCityCreate,
    db: Session = Depends(get_db)
):
    try:
        result = CityService.create_city(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="City created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating City failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=CitySchema.MasterCityResponse,
    dependencies=[check_permission(2, "/cities", "view")],
    status_code=status.HTTP_200_OK
)
def list_cities(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = CityService.get_cities(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Cities fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Cities failed", getattr(e, "status_code", 500))


# -------------- Import Cities ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/cities", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterCities)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Cities failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{city_id}",
    response_model=CitySchema.MasterCityResponse,
    dependencies=[check_permission(2, "/cities", "view")],
    status_code=status.HTTP_200_OK
)
def get_city(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    city_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = CityService.get_city_by_id(db, city_id)
        if not result:
            return handle_exception(Exception("City not found"), "Fetching City by ID failed", 404)
        return Response(
            json_data=result,
            message="City fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch City")


# ---------------- UPDATE ----------------
@router.put(
    "/{city_id}",
    response_model=CitySchema.MasterCityResponse,
    dependencies=[check_permission(2, "/cities", "edit")],
    status_code=status.HTTP_200_OK
)
def update_city(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    city_id: int,
    data: CitySchema.MasterCityUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = CityService.update_city(db, city_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("City not found"), "Updating City failed", 404)
        return Response(
            json_data=updated,
            message="City updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "City update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{city_id}",
    response_model=CitySchema.MasterCityResponse,
    dependencies=[check_permission(2, "/cities", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_city(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    city_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = CityService.delete_city(db, city_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("City not found"), "Deleting City failed", 404)
        return Response(
            json_data=deleted,
            message="City deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting City failed", getattr(e, "status_code", 500))
