from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import user as UserSchemas
from app.utils.responses import Response
from app.services.user_management import user_service as UserService
from app.core.permissions import check_permission
from app.models.user_management.user import User
from app.schemas.user_management.user import UserExportOut
from app.utils.export_helper.common_export_file import transform_users_for_export
from app.utils.export_helper.generic_exporter import export_to_csv
from app.utils.Import_helper.common_import_file import import_csv_to_model

router = APIRouter()

#---------- Helper Function for Consistent Error Handling ----------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return UserSchemas.UserResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

#---------- Create User ----------
@router.post("/", response_model=UserSchemas.UserResponse, dependencies=[check_permission(1, "/users", "create")], status_code=status.HTTP_201_CREATED)
def register_user(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    user: UserSchemas.UserCreate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        result = UserService.create_user(db, user, login_id)
        return Response(
            message="User created successfully",
            status_code=status.HTTP_201_CREATED,
            json_data=result
        )
    except Exception as e:
        return handle_exception(e, "User creation failed", getattr(e, "status_code", 400))

#---------- List Users ----------
@router.get("/", response_model=UserSchemas.UserResponse, dependencies=[check_permission(1, "/users", "view")], status_code=status.HTTP_200_OK)
def list_users(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = UserService.get_users(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result, 
            message="Users fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching users", getattr(e, "status_code", 500))

#---------- Export Users ----------
@router.get("/export",
            response_model=UserSchemas.UserExportOut,
            dependencies=[check_permission(1, "/users", "export")],
            status_code=status.HTTP_200_OK)
def export_users(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        users = db.query(User).all()
        user_schema_list = transform_users_for_export(users)
        return export_to_csv(user_schema_list, UserExportOut, filename="user.csv")
    except Exception as e:
        return handle_exception(e, "User export failed", getattr(e, "status_code", 500))

#---------- Import Users ----------
@router.post("/import-csv/",
             status_code=status.HTTP_200_OK,
             dependencies=[check_permission(1, "/users", "import")])
def import_csv(current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
               file: UploadFile = File(...), 
               db: Session = Depends(get_db)):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, User)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "User import failed", getattr(e, "status_code", 500))

#---------- Fetch Single User by ID ----------
@router.get("/{user_id}", response_model=UserSchemas.UserResponse, dependencies=[check_permission(1, "/users", "view")], status_code=status.HTTP_200_OK)
def fetch_user(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return handle_exception(Exception("User not found"), "Error fetching user", 404)
        return Response(
            json_data=user,
            message="User fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching user", getattr(e, "status_code", 500))

#---------- Update User ----------
@router.put("/{user_id}", response_model=UserSchemas.UserResponse, dependencies=[check_permission(1, "/users", "edit")], status_code=status.HTTP_200_OK)
def update_user_details(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    user_id: int,
    user: UserSchemas.UserUpdate,
    db: Session = Depends(get_db)
):
    try:
        login_id = current_user.id
        updated_user = UserService.update_user(db, user_id, user, login_id)
        if not updated_user:
            return handle_exception(Exception("User not found"), "Error updating user", 404)
        return Response(
            json_data=updated_user,
            message="User updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating user", getattr(e, "status_code", 500))

#---------- Delete User ----------
@router.delete("/{user_id}", response_model=UserSchemas.UserResponse, dependencies=[check_permission(1, "/users", "delete")], status_code=status.HTTP_200_OK)
def delete_user_details(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user)],
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_user = UserService.delete_user(db, user_id)
        if not deleted_user:
            return handle_exception(Exception("User not found"), "Error deleting user", 404)
        return Response(
            json_data=deleted_user,
            message="User deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting user", getattr(e, "status_code", 500))

