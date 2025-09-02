from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class BusinessVerticalBase(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class BusinessVerticalCreate(BusinessVerticalBase):
    pass

class BusinessVerticalUpdate(BusinessVerticalBase):
    pass


# ---------------- Output Schema ----------------
class BusinessVerticalOut(BaseModel):
    id: int
    name: Optional[str] = None
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
class PaginatedBusinessVerticals(BaseModel):
    business_verticals: List[BusinessVerticalOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class BusinessVerticalExportOut(BaseModel):
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
class BusinessVerticalResponse(DefaultResponse):
    data: Optional[Union[BusinessVerticalOut, PaginatedBusinessVerticals, List[BusinessVerticalExportOut]]] = None

    class Config:
        orm_mode = True
