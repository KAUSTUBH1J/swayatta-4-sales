from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user_management import sub_department as SubDeptSchemas
from app.services.user_management import sub_department_service as SubDeptService
from app.core import auth_service as AuthService
from app.utils.responses import Response
from app.core.permissions import check_permission
from app.schemas.user_management.sub_department import SubDepartmentExportOut
from app.models.user_management.sub_department import SubDepartment
from app.utils.export_helper.common_export_file import transform_sub_departments_to_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.utils.Import_helper.common_import_file import import_csv_to_model
from math import ceil

router = APIRouter()

# ---------------- Centralized Exception Handler ----------------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return SubDeptSchemas.SubDepartmentResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

# ---------------- Create ----------------
@router.post(
    "/",
    response_model=SubDeptSchemas.SubDepartmentResponse,
    dependencies=[check_permission(1, "/sub-departments", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_sub_department(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    sub_department: SubDeptSchemas.SubDepartmentCreate,
    db: Session = Depends(get_db),
):
    try:
        result = SubDeptService.create_sub_department(db, sub_department, login_id=current_user.id)
        return Response(
            json_data=result,
            message="SubDepartment created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return handle_exception(e, "SubDepartment creation failed")

# ---------------- List with Pagination & Search ----------------
@router.get(
    "/",
    response_model=SubDeptSchemas.SubDepartmentResponse,
    dependencies=[check_permission(1, "/sub-departments", "view")],
    status_code=status.HTTP_200_OK
)
def list_sub_departments(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
):
    try:
        offset = (page - 1) * limit
        result = SubDeptService.get_sub_departments(db, skip=offset, limit=limit, search=search)
        total_pages = ceil(result["total"] / limit) if result["total"] else 1
        result["total_pages"] = total_pages
        return Response(
            json_data=result,
            message="SubDepartments fetched successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return handle_exception(e, "Error fetching SubDepartments")


# ---------------- Export CSV ----------------
@router.get(
    "/export",
    response_model=SubDeptSchemas.SubDepartmentExportOut,
    dependencies=[check_permission(1, "/sub-departments", "export")],
    status_code=status.HTTP_200_OK
)
def export_subdept(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        sub_dept = db.query(SubDepartment).all()
        sudept_schema_list = transform_sub_departments_to_export(sub_dept)
        return export_to_csv(sudept_schema_list, SubDepartmentExportOut, filename="sub_dept.csv")
    except Exception as e:
        return handle_exception(e, "Sub-department export failed")

# ---------------- Import CSV ----------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(1, "/sub-departments", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, SubDepartment)
        return Response(
            json_data={"inserted_count": inserted_count},
            message=f"{inserted_count} records imported successfully.",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Sub Department import failed")


# ---------------- Get by ID ----------------
@router.get(
    "/{sub_department_id}",
    response_model=SubDeptSchemas.SubDepartmentResponse,
    dependencies=[check_permission(1, "/sub-departments", "view")],
    status_code=status.HTTP_200_OK
)
def fetch_sub_department(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    sub_department_id: int,
    db: Session = Depends(get_db),
):
    try:
        sub_department = SubDeptService.get_sub_department_by_id(db, sub_department_id)
        if not sub_department:
            return handle_exception(Exception("SubDepartment not found"), "Error fetching SubDepartment", 404)
        return Response(
            json_data=sub_department,
            message="SubDepartment fetched successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return handle_exception(e, "Error fetching SubDepartment")

# ---------------- Update ----------------
@router.put(
    "/{sub_department_id}",
    response_model=SubDeptSchemas.SubDepartmentResponse,
    dependencies=[check_permission(1, "/sub-departments", "edit")],
    status_code=status.HTTP_200_OK
)
def update_sub_department_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    sub_department_id: int,
    sub_department: SubDeptSchemas.SubDepartmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_sub_dept = SubDeptService.update_sub_department(db, sub_department_id, sub_department, login_id=current_user.id)
        if not updated_sub_dept:
            return handle_exception(Exception("SubDepartment not found"), "Error updating SubDepartment", 404)
        return Response(
            json_data=updated_sub_dept,
            message="SubDepartment updated successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return handle_exception(e, "Error updating SubDepartment")

# ---------------- Delete (Soft) ----------------
@router.delete(
    "/{sub_department_id}",
    response_model=SubDeptSchemas.SubDepartmentResponse,
    dependencies=[check_permission(1, "/sub-departments", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_sub_department_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    sub_department_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted_sub_dept = SubDeptService.delete_sub_department(db, sub_department_id, login_id=current_user.id)
        if not deleted_sub_dept:
            return handle_exception(Exception("SubDepartment not found"), "Error deleting SubDepartment", 404)
        return Response(
            json_data=deleted_sub_dept,
            message="SubDepartment deleted successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return handle_exception(e, "Error deleting SubDepartment")

