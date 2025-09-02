from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import module as ModuleSchema
from app.utils.responses import Response
from app.services.user_management import module_service as ModuleService
from app.core.permissions import check_permission

router = APIRouter()

# Helper for consistent error handling
def handle_exception(e: Exception, msg: str, code: int = 500):
    return Response(
        message=f"{msg}: {str(e)}",
        status_code=code,
        json_data=None
    )



# ---------------- Create Module ----------------
@router.post("/", response_model=ModuleSchema.ModuleOut,
             dependencies=[check_permission(11, "/modules", "create")],
             status_code=status.HTTP_201_CREATED)
def create_module(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    module: ModuleSchema.ModuleCreate,
    db: Session = Depends(get_db)
):
    try:
        result = ModuleService.create_module(db, module, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Module created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Module failed", getattr(e, "status_code", 500))


# ---------------- List Modules ----------------
@router.get("/", response_model=ModuleSchema.ModuleOut,
            dependencies=[check_permission(11, "/modules", "view")],
            status_code=status.HTTP_200_OK)
def list_modules(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = ModuleService.get_modules(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Modules fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Module failed", getattr(e, "status_code", 500))


# ---------------- Get Module by ID ----------------
@router.get("/{module_id}", response_model=ModuleSchema.ModuleOut,
            dependencies=[check_permission(11, "/modules", "view")],
            status_code=status.HTTP_200_OK)
def fetch_module(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    module_id: int,
    db: Session = Depends(get_db)
):
    try:
        module = ModuleService.get_module_by_id(db, module_id)
        if not module:
            return handle_exception(Exception("Module not found"), "Fetching Module by ID failed" ,404)
        return Response(
            json_data=module,
            message="Module fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Module by ID failed", getattr(e, "status_code", 500))


# ---------------- Update Module ----------------
@router.put("/{module_id}", response_model=ModuleSchema.ModuleOut,
            dependencies=[check_permission(11, "/modules", "edit")],
            status_code=status.HTTP_200_OK)
def update_module_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    module_id: int,
    module: ModuleSchema.ModuleCreate,
    db: Session = Depends(get_db)
):
    try:
        updated_module = ModuleService.update_module(db, module_id, module, login_id=current_user.id)
        if not updated_module:
            return handle_exception(Exception("Module not found"), "Updating Module by ID failed" ,404)
        return Response(
            json_data=updated_module,
            message="Module updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Updating Module by ID failed", getattr(e, "status_code", 500))


# ---------------- Delete Module ----------------
@router.delete("/{module_id}", response_model=ModuleSchema.ModuleOut,
               dependencies=[check_permission(11, "/modules", "delete")],
               status_code=status.HTTP_200_OK)
def delete_module_details(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    module_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_module = ModuleService.delete_module(db, module_id, login_id=current_user.id)
        if not deleted_module:
            return handle_exception(Exception("Module not found"), "Deleting Module by ID failed" ,404)
        return Response(
            json_data=deleted_module,
            message="Module deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Module by ID failed", getattr(e, "status_code", 500))
