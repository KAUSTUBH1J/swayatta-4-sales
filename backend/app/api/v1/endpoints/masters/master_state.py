from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.master_states import MasterStates
from app.schemas.masters import master_state as StateSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_state as StateService
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
    response_model=StateSchema.MasterStateResponse,
    dependencies=[check_permission(2, "/states", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_state(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: StateSchema.MasterStateCreate,
    db: Session = Depends(get_db)
):
    try:
        result = StateService.create_state(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="State created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating State failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=StateSchema.MasterStateResponse,
    dependencies=[check_permission(2, "/states", "view")],
    status_code=status.HTTP_200_OK
)
def list_states(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = StateService.get_states(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="States fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching States failed", getattr(e, "status_code", 500))


# -------------- Import States ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/states", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, MasterStates)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing States failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{state_id}",
    response_model=StateSchema.MasterStateResponse,
    dependencies=[check_permission(2, "/states", "view")],
    status_code=status.HTTP_200_OK
)
def get_state(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    state_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = StateService.get_state_by_id(db, state_id)
        if not result:
            return handle_exception(Exception("State not found"), "Fetching State by ID failed", 404)
        return Response(
            json_data=result,
            message="State fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch State")


# ---------------- UPDATE ----------------
@router.put(
    "/{state_id}",
    response_model=StateSchema.MasterStateResponse,
    dependencies=[check_permission(2, "/states", "edit")],
    status_code=status.HTTP_200_OK
)
def update_state(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    state_id: int,
    data: StateSchema.MasterStateUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = StateService.update_state(db, state_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("State not found"), "Updating State failed", 404)
        return Response(
            json_data=updated,
            message="State updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "State update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{state_id}",
    response_model=StateSchema.MasterStateResponse,
    dependencies=[check_permission(2, "/states", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_state(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    state_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = StateService.delete_state(db, state_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("State not found"), "Deleting State failed", 404)
        return Response(
            json_data=deleted,
            message="State deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting State failed", getattr(e, "status_code", 500))
