from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class RoleBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass


# ---------------- Output Schema (Response) ----------------
class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Display names for created/updated users
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedRoles(BaseModel):
    roles: List[RoleOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ----------- Role Export Schema -------------------
class RoleExportOut(BaseModel):
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
class RoleResponse(DefaultResponse):
    data: Optional[Union[RoleOut, PaginatedRoles, List[RoleExportOut]]] = None

    class Config:
        orm_mode = True
