from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse

# ---------------- Base Schema ----------------
class RegionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False

# ---------------- Create & Update Schemas ----------------
class RegionCreate(RegionBase):
    pass

class RegionUpdate(RegionBase):
    pass

# ---------------- Output Schema ----------------
class RegionOut(RegionBase):
    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True

# ---------------- Paginated List Wrapper ----------------
class PaginatedRegions(BaseModel):
    regions: List[RegionOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True
        
#--------------Region Export Schema-----------------------
class RegionExportOut(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------------- API Response Wrapper ----------------
class RegionResponse(DefaultResponse):
    data: Optional[Union[RegionOut, PaginatedRegions]] = None

    class Config:
        orm_mode = True

