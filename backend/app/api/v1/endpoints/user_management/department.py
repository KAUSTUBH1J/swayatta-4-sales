from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query,UploadFile, File
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import department as DepartmentSchemas
from app.utils.responses import Response
from app.services.user_management import department_service as DepartmentService
from app.core.permissions import check_permission
from app.utils.export_helper.common_export_file import transform_departments_for_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.models.user_management.department import Department
from app.schemas.user_management.department import DepartmentExportOut
from app.utils.Import_helper.common_import_file import import_csv_to_model
router = APIRouter()

# Helper for consistent error handling
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )


# ---------------- Create Department ----------------
@router.post("/", response_model=DepartmentSchemas.DepartmentResponse,
             dependencies=[check_permission(1, "/departments", "create")],
             status_code=status.HTTP_201_CREATED)
def create_department(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    department: DepartmentSchemas.DepartmentCreate,
    db: Session = Depends(get_db)
):
    try:
        result = DepartmentService.create_department(db, department, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Department created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Department failed", getattr(e, "status_code", 500))
        
        


# ---------------- List Departments ----------------
@router.get("/", response_model=DepartmentSchemas.DepartmentResponse,
            dependencies=[check_permission(1, "/departments", "view")],
            status_code=status.HTTP_200_OK)
def list_departments(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = DepartmentService.get_departments(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Departments fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Department failed", getattr(e, "status_code", 500))

#----------------Export Department---------------------
@router.get("/export",
            response_model=DepartmentSchemas.DepartmentExportOut,
            dependencies=[check_permission(1, "/departments", "export")],
            status_code=status.HTTP_200_OK)
def export_department(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        dept = db.query(Department).all()
        dept_schema_list = transform_departments_for_export(dept)
        return export_to_csv(dept_schema_list, DepartmentExportOut, filename="department.csv")
    except Exception as e:
        return handle_exception(e, "Exporting Department failed", getattr(e, "status_code", 500))
        
#--------------Import Department---------------------------
@router.post("/import-csv/",
             status_code=status.HTTP_200_OK,
             dependencies=[check_permission(1, "/departments", "import")])
def import_csv(current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
               file: UploadFile = File(...), 
               db: Session = Depends(get_db)):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, Department)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Department failed", getattr(e, "status_code", 500))


# ---------------- Get Department by ID ----------------
@router.get("/{department_id}", response_model=DepartmentSchemas.DepartmentResponse,
            dependencies=[check_permission(1, "/departments", "view")],
            status_code=status.HTTP_200_OK)
def fetch_department(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    department_id: int,
    db: Session = Depends(get_db)
):
    try:
        department = DepartmentService.get_department_by_id(db, department_id)
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        return Response(
            json_data=department,
            message="Department fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Department by ID failed", getattr(e, "status_code", 500))


# ---------------- Update Department ----------------
@router.put("/{department_id}", response_model=DepartmentSchemas.DepartmentResponse,
            dependencies=[check_permission(1, "/departments", "edit")],
            status_code=status.HTTP_200_OK)
def update_department_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    department_id: int,
    department: DepartmentSchemas.DepartmentCreate,
    db: Session = Depends(get_db)
):
    try:
        updated_department = DepartmentService.update_department(
            db, department_id, department, login_id=current_user.id
        )
        if not updated_department:
            return handle_exception(Exception("Department not found"), "Updating Department failed", 404)
        return Response(
            json_data=updated_department,
            message="Department updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating Department failed", getattr(e, "status_code", 500))


# ---------------- Delete Department ----------------
@router.delete("/{department_id}", response_model=DepartmentSchemas.DepartmentResponse,
               dependencies=[check_permission(1, "/departments", "delete")],
               status_code=status.HTTP_200_OK)
def delete_department_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    department_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_department = DepartmentService.delete_department(db, department_id, login_id=current_user.id)
        if not deleted_department:
            return handle_exception(Exception("Department not found"), "Department Designation failed", 404)
        return Response(
            json_data=deleted_department,
            message="Department deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Department failed", getattr(e, "status_code", 500))

