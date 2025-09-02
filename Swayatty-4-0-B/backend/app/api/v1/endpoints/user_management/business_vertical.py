from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management.business_vertical import (
    BusinessVerticalCreate,
    BusinessVerticalUpdate,
    BusinessVerticalOut,
    BusinessVerticalResponse
)
from app.schemas.user_management.user import UserResponse
from app.services.user_management import business_vertical_service
from app.utils.responses import Response
from app.models.user_management.business_vertical import BusinessVertical

router = APIRouter()

@router.post("/", response_model=BusinessVerticalResponse, status_code=status.HTTP_201_CREATED)
def create_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    vertical: BusinessVerticalCreate,
    db: Session = Depends(get_db)
):
    try:
        result = business_vertical_service.create_business_vertical(db, vertical)
        return Response(json_data=result, message="Business Vertical created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/", response_model=BusinessVerticalResponse)
# def list_business_verticals(
#     current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
#     db: Session = Depends(get_db),
#     limit: int = Query(10, ge=1, le=100),
#     page: int = Query(1, ge=1)
# ):
#     try:
#         offset = (page - 1) * limit
#         result = business_vertical_service.get_all_business_verticals(db)[offset:offset + limit]
#         return Response(json_data=result, message="Business Verticals fetched successfully", status_code=status.HTTP_200_OK)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Error fetching business verticals")




@router.get("/", response_model=BusinessVerticalResponse)
def list_designations(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: str = Query(None)
):
    try:
        offset = (page - 1) * limit

        query = db.query(BusinessVertical).filter(BusinessVertical.is_deleted == False)

        if search:
            query = query.filter(
                or_(
                    BusinessVertical.business_vertical_name.ilike(f"%{search}%"),
                    BusinessVertical.description.ilike(f"%{search}%")
                )
            )

        total = query.count()
        items = query.offset(offset).limit(limit).all()

        result = {
            "items": items,
            "total": total,
            "limit": limit,
            "page": page
        }

        return Response(
            json_data=result,
            message="Business Vertical fetched successfully",
            status_code=status.HTTP_200_OK
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Error fetching Business Vertical")





@router.get("/{vertical_id}", response_model=BusinessVerticalResponse)
def get_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    vertical_id: int,
    db: Session = Depends(get_db)
):
    vertical = business_vertical_service.get_business_vertical_by_id(db, vertical_id)
    if not vertical:
        raise HTTPException(status_code=404, detail="Business Vertical not found")
    return Response(json_data=vertical, message="Business Vertical fetched successfully", status_code=status.HTTP_200_OK)


@router.put("/{vertical_id}", response_model=BusinessVerticalResponse)
def update_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    vertical_id: int,
    vertical_data: BusinessVerticalUpdate,
    db: Session = Depends(get_db)
):
    updated = business_vertical_service.update_business_vertical(db, vertical_id, vertical_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Business Vertical not found")
    return Response(json_data=updated, message="Business Vertical updated successfully", status_code=status.HTTP_200_OK)


@router.delete("/{vertical_id}", response_model=BusinessVerticalResponse)
def delete_business_vertical(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    vertical_id: int,
    db: Session = Depends(get_db)
):
    deleted = business_vertical_service.delete_business_vertical(db, vertical_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Business Vertical not found")
    return Response(json_data=deleted, message="Business Vertical deleted successfully", status_code=status.HTTP_200_OK)
