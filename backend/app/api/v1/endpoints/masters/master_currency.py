from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.schemas.masters import master_currency as CurrencySchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_currency as CurrencyService

router = APIRouter()


# ---------- Create ----------
@router.post(
    "/",
    response_model=CurrencySchema.MasterCurrencyOut,
    dependencies=[check_permission(2, "/currencies", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_currency(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: CurrencySchema.MasterCurrencyCreate,
    db: Session = Depends(get_db)
):
    result = CurrencyService.create_currency(db, data, login_id=current_user.id)
    return Response(json_data=result, message="Currency created successfully", status_code=status.HTTP_201_CREATED)


# ---------- List ----------
@router.get(
    "/",
    response_model=CurrencySchema.PaginatedMasterCurrencies,
    dependencies=[check_permission(2, "/currencies", "view")],
    status_code=status.HTTP_200_OK
)
def list_currencies(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    offset = (page - 1) * limit
    result = CurrencyService.get_currencies(db, skip=offset, limit=limit, search=search)
    return Response(json_data=result, message="Currencies fetched successfully", status_code=status.HTTP_200_OK)


# ---------- Get By ID ----------
@router.get(
    "/{c_id}",
    response_model=CurrencySchema.MasterCurrencyOut,
    dependencies=[check_permission(2, "/currencies", "view")],
    status_code=status.HTTP_200_OK
)
def get_currency(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    c_id: int,
    db: Session = Depends(get_db)
):
    result = CurrencyService.get_currency_by_id(db, c_id)
    if not result:
        return Response(message="Currency not found", status_code=404, json_data=None)
    return Response(json_data=result, message="Currency fetched successfully", status_code=status.HTTP_200_OK)


# ---------- Update ----------
@router.put(
    "/{c_id}",
    response_model=CurrencySchema.MasterCurrencyOut,
    dependencies=[check_permission(2, "/currencies", "edit")],
    status_code=status.HTTP_200_OK
)
def update_currency(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    c_id: int,
    data: CurrencySchema.MasterCurrencyUpdate,
    db: Session = Depends(get_db)
):
    updated = CurrencyService.update_currency(db, c_id, data, login_id=current_user.id)
    if not updated:
        return Response(message="Currency not found", status_code=404, json_data=None)
    return Response(json_data=updated, message="Currency updated successfully", status_code=status.HTTP_200_OK)


# ---------- Delete ----------
@router.delete(
    "/{c_id}",
    response_model=CurrencySchema.MasterCurrencyOut,
    dependencies=[check_permission(2, "/currencies", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_currency(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    c_id: int,
    db: Session = Depends(get_db)
):
    deleted = CurrencyService.delete_currency(db, c_id, login_id=current_user.id)
    if not deleted:
        return Response(message="Currency not found", status_code=404, json_data=None)
    return Response(json_data=deleted, message="Currency deleted successfully", status_code=status.HTTP_200_OK)
