from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.models.masters.product_service_interest import ProductServiceInterest
from app.schemas.masters import product_service_interest as PSSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import product_service_interest as PSService
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
    response_model=PSSchema.ProductServiceInterestResponse,
    dependencies=[check_permission(2, "/product_service_interests", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_product_service_interest(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: PSSchema.ProductServiceInterestCreate,
    db: Session = Depends(get_db)
):
    try:
        result = PSService.create_product_service_interest(db, data, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Product/Service Interest created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Creating Product/Service Interest failed", getattr(e, "status_code", 500))


# ---------------- LIST ----------------
@router.get(
    "/",
    response_model=PSSchema.ProductServiceInterestResponse,
    dependencies=[check_permission(2, "/product_service_interests", "view")],
    status_code=status.HTTP_200_OK
)
def list_product_service_interests(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * limit
        result = PSService.get_product_service_interests(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Product/Service Interests fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Fetching Product/Service Interests failed", getattr(e, "status_code", 500))


# -------------- Import Product/Service Interest ---------------------------
@router.post(
    "/import-csv/",
    status_code=status.HTTP_200_OK,
    dependencies=[check_permission(2, "/product_service_interests", "import")]
)
def import_csv(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = file.file.read()
        inserted_count = import_csv_to_model(file_content, db, ProductServiceInterest)
        return {"message": f"{inserted_count} records imported successfully."}
    except Exception as e:
        return handle_exception(e, "Importing Product/Service Interests failed", getattr(e, "status_code", 500))


# ---------------- GET BY ID ----------------
@router.get(
    "/{ps_id}",
    response_model=PSSchema.ProductServiceInterestResponse,
    dependencies=[check_permission(2, "/product_service_interests", "view")],
    status_code=status.HTTP_200_OK
)
def get_product_service_interest(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ps_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = PSService.get_product_service_interest_by_id(db, ps_id)
        if not result:
            return handle_exception(Exception("Product/Service Interest not found"), "Fetching Product/Service Interest by ID failed", 404)
        return Response(
            json_data=result,
            message="Product/Service Interest fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Failed to fetch Product/Service Interest")


# ---------------- UPDATE ----------------
@router.put(
    "/{ps_id}",
    response_model=PSSchema.ProductServiceInterestResponse,
    dependencies=[check_permission(2, "/product_service_interests", "edit")],
    status_code=status.HTTP_200_OK
)
def update_product_service_interest(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ps_id: int,
    data: PSSchema.ProductServiceInterestUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated = PSService.update_product_service_interest(db, ps_id, data, login_id=current_user.id)
        if not updated:
            return handle_exception(Exception("Product/Service Interest not found"), "Updating Product/Service Interest failed", 404)
        return Response(
            json_data=updated,
            message="Product/Service Interest updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Product/Service Interest update failed")


# ---------------- DELETE ----------------
@router.delete(
    "/{ps_id}",
    response_model=PSSchema.ProductServiceInterestResponse,
    dependencies=[check_permission(2, "/product_service_interests", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_product_service_interest(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    ps_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted = PSService.delete_product_service_interest(db, ps_id, login_id=current_user.id)
        if not deleted:
            return handle_exception(Exception("Product/Service Interest not found"), "Deleting Product/Service Interest failed", 404)
        return Response(
            json_data=deleted,
            message="Product/Service Interest deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Deleting Product/Service Interest failed", getattr(e, "status_code", 500))
