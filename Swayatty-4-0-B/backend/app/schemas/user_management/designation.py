from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class DesignationBase(BaseModel):
    name: str = Field(..., min_length=3)   # 👈 changed to match model
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(DesignationBase):
    pass


# ---------------- Output Schema ----------------
class DesignationOut(BaseModel):
    id: int
    name: Optional[str] = None   # 👈 updated
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedDesignations(BaseModel):
    designations: List[DesignationOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class DesignationExportOut(BaseModel):
    name: str   # 👈 updated
    description: Optional[str] = None
    is_active: Optional[bool] = True

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class DesignationResponse(DefaultResponse):
    data: Optional[Union[DesignationOut, PaginatedDesignations, List[DesignationExportOut]]] = None

    class Config:
        orm_mode = True
