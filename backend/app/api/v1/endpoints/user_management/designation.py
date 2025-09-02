from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query,UploadFile, File
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import designation as DesignationSchemas
from app.utils.responses import Response
from app.services.user_management import designation_service as DesignationService
from app.core.permissions import check_permission
from app.utils.export_helper.common_export_file import transform_designations_to_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.models.user_management.designation import Designation
from app.schemas.user_management.designation import DesignationExportOut
from app.utils.Import_helper.common_import_file import import_csv_to_model

router = APIRouter()

# ---------------- Helper for consistent error handling ----------------

def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )


# ---------------- Create Designation ----------------
@router.post("/", response_model=DesignationSchemas.DesignationResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[check_permission(1, "/designations", "create")])
def create_designation(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    designation: DesignationSchemas.DesignationCreate,
    db: Session = Depends(get_db)
):
    try:
        result = DesignationService.create_designation(db, designation, login_id=current_user.id)
        return Response(json_data=result, message="Designation created", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return handle_exception(e, "Creating Designation failed", getattr(e, "status_code", 500))
        
    
# ---------------- List Designations ----------------
@router.get("/",
            dependencies=[check_permission(1, "/designations", "view")],
            status_code=status.HTTP_200_OK)
def list_designations(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = DesignationService.get_designations(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Designations fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Designation failed", getattr(e, "status_code", 500))

#---------------------Export Designations-------------
@router.get("/export",
            response_model=DesignationSchemas.DesignationExportOut,
            dependencies=[check_permission(1, "/designations", "export")],
            status_code=status.HTTP_200_OK)
def export_designation(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        designation = db.query(Designation).all()
        user_schema_list = transform_designations_to_export(designation)
        return export_to_csv(user_schema_list, DesignationExportOut, filename="designation.csv")
    except Exception as e:
        return handle_exception(e, "Exporting Designation failed", getattr(e, "status_code", 500))
        
        
#--------------Import Designation---------------------------
@router.post("/import-csv/",
             status_code=status.HTTP_200_OK,
             dependencies=[check_permission(1, "/designations", "import")])
def import_csv(current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
               file: UploadFile = File(...), 
               db: Session = Depends(get_db)):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, Designation)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Designation failed", getattr(e, "status_code", 500))
        
# ---------------- Get Designation by ID ----------------
@router.get("/{designation_id}", response_model=DesignationSchemas.DesignationResponse,
            dependencies=[check_permission(1, "/designations", "view")],
            status_code=status.HTTP_200_OK)
def fetch_designation(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    designation_id: int,
    db: Session = Depends(get_db)
):
    try:
        designation = DesignationService.get_designation_by_id(db, designation_id)
        if not designation:
            return handle_exception(Exception("Designation not found"), "Fetching Designation by ID failed" ,404)
        return Response(
            json_data=designation,
            message="Designation fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Designation by ID failed", getattr(e, "status_code", 500))


# ---------------- Update Designation ----------------
@router.put("/{designation_id}", response_model=DesignationSchemas.DesignationResponse,
            dependencies=[check_permission(1, "/designations", "edit")],
            status_code=status.HTTP_200_OK)
def update_designation(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    designation_id: int,
    designation: DesignationSchemas.DesignationUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = DesignationService.update_designation(db, designation_id, designation, current_user.id)
        if not updated:
            return handle_exception(Exception("Designation not found"), "Updating Designation failed", 404)
        return Response(
            json_data=updated,
            message="Designation updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating Designation failed", getattr(e, "status_code", 500))


# ---------------- Delete Designation ----------------
@router.delete("/{designation_id}", response_model=DesignationSchemas.DesignationResponse,
               dependencies=[check_permission(1, "/designations", "delete")],
               status_code=status.HTTP_200_OK)
def delete_designation(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    designation_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = DesignationService.delete_designation(db, designation_id, current_user.id)
        if not deleted:
            return handle_exception(Exception("Designation not found"), "Deleting Designation failed", 404)
        return Response(
            json_data=deleted,
            message="Designation deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Designation failed", getattr(e, "status_code", 500))

