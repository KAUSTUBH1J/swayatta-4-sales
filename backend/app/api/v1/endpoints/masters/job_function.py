from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query,UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_job_function import JobFunction
from app.schemas.masters.job_function import JobFunctionResponse,JobFunctionCreate,JobFunctionUpdate,JobFunctionExportOut
from app.schemas.masters import job_function as JFSchema
from app.schemas.user_management.user import UserResponse
# from app.schemas.masters.business_vertical import BusinessVerticalExportOut
from app.services.masters import job_function as JFService
# from app.utils.export_helper.common_export_file import transform_business_verticals_for_export
# from app.utils.export_helper.generic_exporter import export_to_csv
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
    response_model=JFSchema.JobFunctionResponse,
    dependencies=[check_permission(2, "/job_functions", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_job_function(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: JFSchema.JobFunctionCreate,
    db: Session = Depends(get_db)
):
    try:
        result = JFService.create_job_function(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Job Function created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating JF failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=JFSchema.JobFunctionResponse,
    dependencies=[check_permission(2, "/job_functions", "view")],
    status_code=status.HTTP_200_OK
)
def list_job_functions(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = JFService.get_job_functions(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Job Functions fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching JF failed", getattr(e, "status_code", 500))

#-------------------Export BusinessVertical-----------------------
# @router.get("/export",
#     response_model=JFSchema.JobFunctionExportOut,
#     dependencies=[check_permission(1, "/job_functions", "export")],
#     status_code=status.HTTP_200_OK)
# def export_job_functions(
#     current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
#     db: Session = Depends(get_db),
# ):
#     try:
#         jobfunction = db.query(JobFunction).all()
#         bjob_function_list = transform_business_verticals_for_export(businessvertical)
#         return export_to_csv(business_vertical_list, JobFunctionExportOut, filename="business_vertical.csv")
#     except Exception as e:
#         return handle_exception(e, "Exporting BV failed", getattr(e, "status_code", 500))



#--------------Import Job Function---------------------------
@router.post("/import-csv/",
             status_code=status.HTTP_200_OK,
             dependencies=[check_permission(2, "/job_functions", "import")])
def import_csv(current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
               file: UploadFile = File(...), 
               db: Session = Depends(get_db)):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, JobFunction)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing JF failed", getattr(e, "status_code", 500))
        
# ---------------- GET BY ID ----------------
@router.get(
    "/{bv_id}",
    response_model=JFSchema.JobFunctionResponse,
    dependencies=[check_permission(2, "/job_functions", "view")],
    status_code=status.HTTP_200_OK
)
def get_job_function(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = JFService.get_job_function_by_id(db, bv_id)
        if not result:
            return handle_exception(Exception("Job Function not found"), "Fetching job by ID failed" ,404)
        return Response(
            json_data=result,
            message="Job Function fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        handle_exception(e, "Failed to fetch job function")



# # ---------------- UPDATE ----------------
@router.put(
    "/{bv_id}",
    response_model=JFSchema.JobFunctionResponse,
    dependencies=[check_permission(2, "/job_functions", "edit")],
    status_code=status.HTTP_200_OK
)
def update_job_function(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    data: JFSchema.JobFunctionUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = JFService.update_job_function(db, bv_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Job Function  not found"), "Updating JF failed", 404)
        return Response(
            json_data=updated,
            message="Job Function updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        handle_exception(e, "Job Function update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{bv_id}",
    response_model=JFSchema.JobFunctionResponse,
    dependencies=[check_permission(2, "/job_functions", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_job_function(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    bv_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = JFService.delete_job_function(db, bv_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("job function not found"), "Deleting JF failed", 404)
        return Response(
            json_data=deleted,
            message="Job Function deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting JF failed", getattr(e, "status_code", 500))

