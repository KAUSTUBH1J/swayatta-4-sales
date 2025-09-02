from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    pass


# ---------------- Output Schema ----------------
class PermissionOut(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    # Display names for created/updated users
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedPermissions(BaseModel):
    permissions: List[PermissionOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class PermissionExportOut(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class PermissionResponse(DefaultResponse):
    data: Optional[Union[PermissionOut, PaginatedPermissions, List[PermissionExportOut]]] = None

    class Config:
        orm_mode = True
