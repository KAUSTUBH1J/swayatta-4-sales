from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_sub_industry_segment import MasterSubIndustrySegments
from app.schemas.masters import master_sub_industry_segment as MSISchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_sub_industry_segment as MSIService
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
    response_model=MSISchema.MasterSubIndustrySegmentResponse,
    dependencies=[check_permission(2, "/sub_industry_segments", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_master_sub_industry_segment(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: MSISchema.MasterSubIndustrySegmentCreate,
    db: Session = Depends(get_db)
):
    try:
        result = MSIService.create_master_sub_industry_segment(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Sub Industry Segment created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Sub Industry Segment failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=MSISchema.MasterSubIndustrySegmentResponse,
    dependencies=[check_permission(2, "/sub_industry_segments", "view")],
    status_code=status.HTTP_200_OK
)
def list_master_sub_industry_segments(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = MSIService.get_master_sub_industry_segments(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Sub Industry Segments fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Sub Industry Segments failed", getattr(e, "status_code", 500))


# -------------- Import Sub Industry Segments ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/sub_industry_segments", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterSubIndustrySegments)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Sub Industry Segments failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{msis_id}",
    response_model=MSISchema.MasterSubIndustrySegmentResponse,
    dependencies=[check_permission(2, "/sub_industry_segments", "view")],
    status_code=status.HTTP_200_OK
)
def get_master_sub_industry_segment(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    msis_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = MSIService.get_master_sub_industry_segment_by_id(db, msis_id)
        if not result:
            return handle_exception(Exception("Sub Industry Segment not found"), "Fetching Sub Industry Segment by ID failed", 404)
        return Response(
            json_data=result,
            message="Sub Industry Segment fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Sub Industry Segment")


# ---------------- UPDATE ----------------
@router.put(
    "/{msis_id}",
    response_model=MSISchema.MasterSubIndustrySegmentResponse,
    dependencies=[check_permission(2, "/sub_industry_segments", "edit")],
    status_code=status.HTTP_200_OK
)
def update_master_sub_industry_segment(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    msis_id: int,
    data: MSISchema.MasterSubIndustrySegmentUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = MSIService.update_master_sub_industry_segment(db, msis_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Sub Industry Segment not found"), "Updating Sub Industry Segment failed", 404)
        return Response(
            json_data=updated,
            message="Sub Industry Segment updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Sub Industry Segment update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{msis_id}",
    response_model=MSISchema.MasterSubIndustrySegmentResponse,
    dependencies=[check_permission(2, "/sub_industry_segments", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_master_sub_industry_segment(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    msis_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = MSIService.delete_master_sub_industry_segment(db, msis_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Sub Industry Segment not found"), "Deleting Sub Industry Segment failed", 404)
        return Response(
            json_data=deleted,
            message="Sub Industry Segment deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Sub Industry Segment failed", getattr(e, "status_code", 500))
