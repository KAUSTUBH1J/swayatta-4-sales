from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query,UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.business_vertical import BusinessVertical
from app.schemas.user_management.user import UserResponse
from app.schemas.masters import business_vertical as BVSchema
from app.schemas.masters.business_vertical import BusinessVerticalExportOut
from app.services.masters import business_vertical_service as BVService
from app.utils.export_helper.common_export_file import transform_business_verticals_for_export
from app.utils.export_helper.generic_exporter import export_to_csv
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
    response_model=BVSchema.BusinessVerticalResponse,
    dependencies=[check_permission(1, "/business-verticals", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: BVSchema.BusinessVerticalCreate,
    db: Session = Depends(get_db)
):
    try:
        result = BVService.create_business_vertical(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Business vertical created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating BV failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=BVSchema.BusinessVerticalResponse,
    dependencies=[check_permission(1, "/business-verticals", "view")],
    status_code=status.HTTP_200_OK
)
def list_business_verticals(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = BVService.get_business_verticals(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Business verticals fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching BV failed", getattr(e, "status_code", 500))

#-------------------Export BusinessVertical-----------------------
@router.get("/export",
    response_model=BVSchema.BusinessVerticalExportOut,
    dependencies=[check_permission(1, "/business-verticals", "export")],
    status_code=status.HTTP_200_OK)
def export_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        businessvertical = db.query(BusinessVertical).all()
        business_vertical_list = transform_business_verticals_for_export(businessvertical)
        return export_to_csv(business_vertical_list, BusinessVerticalExportOut, filename="business_vertical.csv")
    except Exception as e:
        return handle_exception(e, "Exporting BV failed", getattr(e, "status_code", 500))



#--------------Import BusinessVertical---------------------------
@router.post("/import-csv/",
             status_code=status.HTTP_200_OK,
             dependencies=[check_permission(1, "/business-verticals", "import")])
def import_csv(current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
               file: UploadFile = File(...), 
               db: Session = Depends(get_db)):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, BusinessVertical)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing BV failed", getattr(e, "status_code", 500))
        
# ---------------- GET BY ID ----------------
@router.get(
    "/{bv_id}",
    response_model=BVSchema.BusinessVerticalResponse,
    dependencies=[check_permission(1, "/business-verticals", "view")],
    status_code=status.HTTP_200_OK
)
def get_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = BVService.get_business_vertical_by_id(db, bv_id)
        if not result:
            return handle_exception(Exception("BussinessVertical not found"), "Fetching role by ID failed" ,404)
        return Response(
            json_data=result,
            message="Business vertical fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        handle_exception(e, "Failed to fetch business vertical")



# # ---------------- UPDATE ----------------
@router.put(
    "/{bv_id}",
    response_model=BVSchema.BusinessVerticalResponse,
    dependencies=[check_permission(1, "/business-verticals", "edit")],
    status_code=status.HTTP_200_OK
)
def update_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    data: BVSchema.BusinessVerticalUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = BVService.update_business_vertical(db, bv_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Business Vertical not found"), "Updating BV failed", 404)
        return Response(
            json_data=updated,
            message="Business vertical updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        handle_exception(e, "Business vertical update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{bv_id}",
    response_model=BVSchema.BusinessVerticalResponse,
    dependencies=[check_permission(1, "/business-verticals", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = BVService.delete_business_vertical(db, bv_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Business vertical not found"), "Deleting BV failed", 404)
        return Response(
            json_data=deleted,
            message="Business vertical deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting BV failed", getattr(e, "status_code", 500))

