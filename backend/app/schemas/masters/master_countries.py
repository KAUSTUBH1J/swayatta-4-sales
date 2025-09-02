from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class MasterCountryBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class MasterCountryCreate(MasterCountryBase):
    pass


class MasterCountryUpdate(MasterCountryBase):
    pass


# ---------------- Output Schema ----------------
class MasterCountryOut(BaseModel):
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
class PaginatedMasterCountries(BaseModel):
    master_countries: List[MasterCountryOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class MasterCountryExportOut(BaseModel):
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
class MasterCountryResponse(DefaultResponse):
    data: Optional[Union[
        MasterCountryOut,
        PaginatedMasterCountries,
        List[MasterCountryExportOut]
    ]] = None

    class Config:
        orm_mode = True
