from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema (Request Validation) ----------------
class MenuBase(BaseModel):
    name: str = Field(..., min_length=2)
    path: Optional[str] = None
    parent_id: Optional[int] = None
    module_id: Optional[int] = None
    order_index: Optional[int] = 0
    icon: Optional[str] = None
    is_sidebar: Optional[bool] = True
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class MenuCreate(MenuBase):
    pass

class MenuUpdate(MenuBase):
    pass


# ---------------- Output Schema (Response) ----------------
class MenuOut(BaseModel):
    id: int
    name: Optional[str] = None
    path: Optional[str] = None
    module_id: Optional[int] = None
    module_name: Optional[str] = None
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    order_index: Optional[int] = None
    icon: Optional[str] = None
    is_sidebar: Optional[bool] = True
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Foreign key display names
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedMenus(BaseModel):
    menus: List[MenuOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class MenuExportOut(BaseModel):
    name: str
    path: Optional[str] = None
    module_name: Optional[str] = None
    parent_name: Optional[str] = None
    order_index: Optional[int] = None
    icon: Optional[str] = None
    is_sidebar: Optional[bool] = True
    is_active: Optional[bool] = True
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class MenuResponse(DefaultResponse):
    data: Optional[Union[MenuOut, PaginatedMenus, List[MenuExportOut]]] = None

    class Config:
        orm_mode = True
