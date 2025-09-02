from typing import Optional, Annotated
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.schemas.masters import region as RegionSchemas
from app.services.masters import region_service as RegionService
from app.schemas.masters.region import RegionExportOut
from app.models.masters.region import Region
from app.utils.export_helper.common_export_file import transform_regions_for_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.utils.Import_helper.common_import_file import import_csv_to_model

router = APIRouter()

# ---------------- Helper Function ----------------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return RegionSchemas.RegionResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

# ---------------- Create Region ----------------
@router.post(
    "/", 
    response_model=RegionSchemas.RegionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[check_permission(1, "/regions", "create")]
)
def create_region(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    region: RegionSchemas.RegionCreate,
    db: Session = Depends(get_db)
):
    try:
        result = RegionService.create_region(db, region, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Region created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Region creation failed", getattr(e, "status_code", 400))

# ---------------- Export Region ----------------
@router.get(
    "/export",
    response_model=RegionSchemas.RegionExportOut,
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "export")]
)
def export_region(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        regions = db.query(Region).all()
        region_schema_list = transform_regions_for_export(regions)
        return export_to_csv(region_schema_list, RegionExportOut, filename="region.csv")
    except Exception as e:
        return handle_exception(e, "Region export failed", getattr(e, "status_code", 500))

# ---------------- Import Region ----------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "import")]
)
def import_region_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, Region)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Region import failed", getattr(e, "status_code", 500))

# ---------------- List Regions ----------------
@router.get(
    "/",
    response_model=RegionSchemas.RegionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "view")]
)
def list_regions(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = None
):
    try:
        skip = (page - 1) * limit
        result = RegionService.get_regions(db, skip=skip, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Regions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching regions failed", getattr(e, "status_code", 500))

# ---------------- Get Region by ID ----------------
@router.get(
    "/{region_id}",
    response_model=RegionSchemas.RegionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "view")]
)
def get_region_by_id(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    region_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = RegionService.get_region_by_id(db, region_id)
        if not result:
            return handle_exception(Exception("Region not found"), "Fetching region failed", 404)
        return Response(
            json_data=result,
            message="Region fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching region failed", getattr(e, "status_code", 500))

# ---------------- Update Region ----------------
@router.put(
    "/{region_id}",
    response_model=RegionSchemas.RegionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "edit")]
)
def update_region(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    region_id: int,
    region: RegionSchemas.RegionUpdate,
    db: Session = Depends(get_db)
):
    try:
        result = RegionService.update_region(db, region_id, region, login_id=current_user.id)
        if not result:
            return handle_exception(Exception("Region not found"), "Updating region failed", 404)
        return Response(
            json_data=result,
            message="Region updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating region failed", getattr(e, "status_code", 500))

# ---------------- Delete Region ----------------
@router.delete(
    "/{region_id}",
    response_model=RegionSchemas.RegionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/regions", "delete")]
)
def delete_region(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    region_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = RegionService.delete_region(db, region_id, login_id=current_user.id)
        if not result:
            return handle_exception(Exception("Region not found"), "Deleting region failed", 404)
        return Response(
            json_data=result,
            message="Region deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting region failed", getattr(e, "status_code", 500))
