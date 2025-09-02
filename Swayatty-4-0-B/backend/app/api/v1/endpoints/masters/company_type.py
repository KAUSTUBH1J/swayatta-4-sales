from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.company_type import CompanyTypeMaster
from app.schemas.user_management.user import UserResponse
from app.schemas.masters import company_type as CTSchema
from app.schemas.masters.company_type import CompanyTypeExportOut
from app.services.masters import company_type as CTService
# from app.utils.export_helper.common_export_file import transform_company_types_for_export
# from app.utils.export_helper.generic_exporter import export_to_csv
# from app.utils.Import_helper.common_import_file import import_csv_to_model

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
    response_model=CTSchema.CompanyTypeResponse,
    dependencies=[check_permission(2, "/company_types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_company_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: CTSchema.CompanyTypeCreate,
    db: Session = Depends(get_db)
):
    try:
        result = CTService.create_company_type(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Company type created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating company type failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=CTSchema.CompanyTypeResponse,
    dependencies=[check_permission(2, "/company_types", "view")],
    status_code=status.HTTP_200_OK
)
def list_company_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = CTService.get_company_types(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Company types fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching company types failed", getattr(e, "status_code", 500))


# ---------------- EXPORT ----------------
@router.get(
    "/export",
    response_model=CTSchema.CompanyTypeExportOut,
    dependencies=[check_permission(2, "/company_types", "export")],
    status_code=status.HTTP_200_OK
)
def export_company_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        company_types = db.query(CompanyTypeMaster).all()
        company_type_list = transform_company_types_for_export(company_types)
        return export_to_csv(company_type_list, CompanyTypeExportOut, filename="company_type.csv")
    except Exception as e:
        return handle_exception(e, "Exporting company types failed", getattr(e, "status_code", 500))


# ---------------- IMPORT ----------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/company_types", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, CompanyType)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing company types failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{ct_id}",
    response_model=CTSchema.CompanyTypeResponse,
    dependencies=[check_permission(2, "/company_types", "view")],
    status_code=status.HTTP_200_OK
)
def get_company_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ct_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = CTService.get_company_type_by_id(db, ct_id)
        if not result:
            return handle_exception(Exception("CompanyType not found"), "Fetching company type by ID failed", 404)
        return Response(
            json_data=result,
            message="Company type fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch company type")


# ---------------- UPDATE ----------------
@router.put(
    "/{ct_id}",
    response_model=CTSchema.CompanyTypeResponse,
    dependencies=[check_permission(2, "/company_types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_company_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ct_id: int,
    data: CTSchema.CompanyTypeUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = CTService.update_company_type(db, ct_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Company type not found"), "Updating company type failed", 404)
        return Response(
            json_data=updated,
            message="Company type updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Company type update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{ct_id}",
    response_model=CTSchema.CompanyTypeResponse,
    dependencies=[check_permission(2, "/company_types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_company_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ct_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = CTService.delete_company_type(db, ct_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Company type not found"), "Deleting company type failed", 404)
        return Response(
            json_data=deleted,
            message="Company type deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting company type failed", getattr(e, "status_code", 500))
