from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management.region import RegionCreate, RegionUpdate, RegionOut,RegionResponse
from app.schemas.user_management.user import UserResponse
from app.services.user_management import region_service
from app.utils.responses import Response
from app.models.user_management.region import Region

router = APIRouter()

@router.post("/", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    region: RegionCreate,
    db: Session = Depends(get_db)
):
    try:
        result = region_service.create_region(db, region)
        return Response(json_data=result, message="Region created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.get("/", response_model=RegionResponse)
# def list_regions(
#     current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
#     db: Session = Depends(get_db),
#     limit: int = Query(10, ge=1, le=100),
#     page: int = Query(1, ge=1)
# ):
#     try:
#         offset = (page - 1) * limit
#         result = region_service.get_all_regions(db)[offset:offset+limit]  # Manual pagination
#         return Response(json_data=result, message="Regions fetched successfully", status_code=status.HTTP_200_OK)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Error fetching regions")


@router.get("/", response_model=RegionResponse)
def list_regions(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: str = Query(None)
):
    try:
        offset = (page - 1) * limit

        query = db.query(Region).filter(Region.is_deleted == False)

        if search:
            query = query.filter(
                or_(
                    Region.region_name.ilike(f"%{search}%"),
                    Region.description.ilike(f"%{search}%")
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
            message="Regions fetched successfully",
            status_code=status.HTTP_200_OK
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Error fetching regions")

@router.get("/{region_id}", response_model=RegionResponse)
def get_region(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    region_id: int,
    db: Session = Depends(get_db)
):
    region = region_service.get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return Response(json_data=region, message="Region fetched successfully", status_code=status.HTTP_200_OK)

@router.put("/{region_id}", response_model=RegionResponse)
def update_region(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    region_id: int,
    region_data: RegionUpdate,
    db: Session = Depends(get_db)
):
    updated = region_service.update_region(db, region_id, region_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Region not found")
    return Response(json_data=updated, message="Region updated successfully", status_code=status.HTTP_200_OK)

@router.delete("/{region_id}", response_model=RegionResponse)
def delete_region(
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    region_id: int,
    db: Session = Depends(get_db)
):
    deleted = region_service.delete_region(db, region_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Region not found")
    return Response(json_data=deleted, message="Region deleted successfully", status_code=status.HTTP_200_OK)
