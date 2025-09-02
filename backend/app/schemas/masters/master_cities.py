from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class MasterCityBase(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class MasterCityCreate(MasterCityBase):
    pass


class MasterCityUpdate(MasterCityBase):
    pass


# ---------------- Output Schema ----------------
class MasterCityOut(BaseModel):
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
class PaginatedMasterCities(BaseModel):
    master_cities: List[MasterCityOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class MasterCityExportOut(BaseModel):
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
class MasterCityResponse(DefaultResponse):
    data: Optional[Union[
        MasterCityOut,
        PaginatedMasterCities,
        List[MasterCityExportOut]
    ]] = None

    class Config:
        orm_mode = True
