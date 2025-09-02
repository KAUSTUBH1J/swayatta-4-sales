from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.head_of_company import HeadCompanyMaster
from app.schemas.user_management.user import UserResponse
from app.schemas.masters import head_of_company as HCSchema
from app.schemas.masters.head_of_company import HeadCompanyExportOut
from app.services.masters import head_of_company as HCService
# from app.utils.export_helper.common_export_file import transform_head_companies_for_export
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
    response_model=HCSchema.HeadCompanyResponse,
    dependencies=[check_permission(2, "/head_companies", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_head_company(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: HCSchema.HeadCompanyCreate,
    db: Session = Depends(get_db)
):
    try:
        result = HCService.create_head_company(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Head company created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating head company failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=HCSchema.HeadCompanyResponse,
    dependencies=[check_permission(2, "/head_companies", "view")],
    status_code=status.HTTP_200_OK
)
def list_head_companies(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = HCService.get_head_companies(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Head companies fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching head companies failed", getattr(e, "status_code", 500))


# ---------------- EXPORT ----------------
@router.get(
    "/export",
    response_model=HCSchema.HeadCompanyExportOut,
    dependencies=[check_permission(2, "/head_companies", "export")],
    status_code=status.HTTP_200_OK
)
def export_head_company(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        head_companies = db.query(HeadCompanyMaster).all()
        head_company_list = transform_head_companies_for_export(head_companies)
        return export_to_csv(head_company_list, HeadCompanyExportOut, filename="head_company.csv")
    except Exception as e:
        return handle_exception(e, "Exporting head companies failed", getattr(e, "status_code", 500))


# ---------------- IMPORT ----------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/head_companies", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, HeadCompanyMaster)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing head companies failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{hc_id}",
    response_model=HCSchema.HeadCompanyResponse,
    dependencies=[check_permission(2, "/head_companies", "view")],
    status_code=status.HTTP_200_OK
)
def get_head_company(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    hc_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = HCService.get_head_company_by_id(db, hc_id)
        if not result:
            return handle_exception(Exception("Head company not found"), "Fetching head company by ID failed", 404)
        return Response(
            json_data=result,
            message="Head company fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch head company")


# ---------------- UPDATE ----------------
@router.put(
    "/{hc_id}",
    response_model=HCSchema.HeadCompanyResponse,
    dependencies=[check_permission(2, "/head_companies", "edit")],
    status_code=status.HTTP_200_OK
)
def update_head_company(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    hc_id: int,
    data: HCSchema.HeadCompanyUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = HCService.update_head_company(db, hc_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Head company not found"), "Updating head company failed", 404)
        return Response(
            json_data=updated,
            message="Head company updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Head company update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{hc_id}",
    response_model=HCSchema.HeadCompanyResponse,
    dependencies=[check_permission(2, "/head_companies", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_head_company(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    hc_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = HCService.delete_head_company(db, hc_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Head company not found"), "Deleting head company failed", 404)
        return Response(
            json_data=deleted,
            message="Head company deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting head company failed", getattr(e, "status_code", 500))
