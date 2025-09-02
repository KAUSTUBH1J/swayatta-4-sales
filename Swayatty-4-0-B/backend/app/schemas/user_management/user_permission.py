from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class UserPermissionBase(BaseModel):
    user_id: int
    module_id: int
    menu_id: int
    permission_ids: str = Field(..., description="Comma separated permission IDs, e.g. '1,2,3'")
    is_active: Optional[bool] = True


# ---------------- Create & Update ----------------
class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermissionUpdate(UserPermissionBase):
    pass

# ---------------- Output Schema ----------------
class UserPermissionOut(BaseModel):
    id: int
    user_name: Optional[str] = None
    module_name: Optional[str] = None
    menu_name: Optional[str] = None
    permission_names: List[str] = Field(default_factory=list)
    is_deleted: Optional[bool] = False

    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedUserPermissions(BaseModel):
    user_permissions: List[UserPermissionOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class UserPermissionExportOut(BaseModel):
    user_name: Optional[str] = None
    module_name: Optional[str] = None
    menu_name: Optional[str] = None
    permission_names: List[str] = Field(default_factory=list)
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- Multiple Create ----------------
class MultiUserPermissionCreate(BaseModel):
    user_permissions: List[UserPermissionCreate]


# ---------------- API Response ----------------
class UserPermissionResponse(DefaultResponse):
    data: Optional[Union[UserPermissionOut, PaginatedUserPermissions, List[UserPermissionExportOut]]] = None

    class Config:
        orm_mode = True
