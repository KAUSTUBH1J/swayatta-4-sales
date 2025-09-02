from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.core.permissions import check_permission
from app.utils.responses import Response
from app.schemas.masters import master_document_type as DocSchema
from app.schemas.user_management.user import UserResponse
from app.services.masters import master_document_type as DocService

router = APIRouter()


# ---------- Create ----------
@router.post(
    "/",
    response_model=DocSchema.DocumentTypeResponse,
    dependencies=[check_permission(2, "/document-types", "create")],
    status_code=status.HTTP_201_CREATED
)
def create_document_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    data: DocSchema.DocumentTypeCreate,
    db: Session = Depends(get_db)
):
    result = DocService.create_document_type(db, data, login_id=current_user.id)
    return Response(json_data=result, message="DocumentType created successfully", status_code=status.HTTP_201_CREATED)


# ---------- List ----------
@router.get(
    "/",
    response_model=DocSchema.DocumentTypeResponse,
    dependencies=[check_permission(2, "/document-types", "view")],
    status_code=status.HTTP_200_OK
)
def list_document_types(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None)
):
    offset = (page - 1) * limit
    result = DocService.get_document_types(db, skip=offset, limit=limit, search=search)
    return Response(json_data=result, message="DocumentTypes fetched successfully", status_code=status.HTTP_200_OK)


# ---------- Get By ID ----------
@router.get(
    "/{doc_id}",
    response_model=DocSchema.DocumentTypeResponse,
    dependencies=[check_permission(2, "/document-types", "view")],
    status_code=status.HTTP_200_OK
)
def get_document_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    doc_id: int,
    db: Session = Depends(get_db)
):
    result = DocService.get_document_type_by_id(db, doc_id)
    if not result:
        return Response(message="DocumentType not found", status_code=404, json_data=None)
    return Response(json_data=result, message="DocumentType fetched successfully", status_code=status.HTTP_200_OK)


# ---------- Update ----------
@router.put(
    "/{doc_id}",
    response_model=DocSchema.DocumentTypeResponse,
    dependencies=[check_permission(2, "/document-types", "edit")],
    status_code=status.HTTP_200_OK
)
def update_document_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    doc_id: int,
    data: DocSchema.DocumentTypeUpdate,
    db: Session = Depends(get_db)
):
    updated = DocService.update_document_type(db, doc_id, data, login_id=current_user.id)
    if not updated:
        return Response(message="DocumentType not found", status_code=404, json_data=None)
    return Response(json_data=updated, message="DocumentType updated successfully", status_code=status.HTTP_200_OK)


# ---------- Delete ----------
@router.delete(
    "/{doc_id}",
    response_model=DocSchema.DocumentTypeResponse,
    dependencies=[check_permission(2, "/document-types", "delete")],
    status_code=status.HTTP_200_OK
)
def delete_document_type(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    doc_id: int,
    db: Session = Depends(get_db)
):
    deleted = DocService.delete_document_type(db, doc_id, login_id=current_user.id)
    if not deleted:
        return Response(message="DocumentType not found", status_code=404, json_data=None)
    return Response(json_data=deleted, message="DocumentType deleted successfully", status_code=status.HTTP_200_OK)
