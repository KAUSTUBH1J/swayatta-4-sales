from pydantic import BaseModel
from typing import Optional, Union, List
from .DefaultResponse import DefaultResponse  # assuming this is defined properly
from datetime import datetime
from enum import Enum

# -----------------------------
# Region Status Enum (Optional, for future-proofing)
# -----------------------------


# -----------------------------
# Base Region Schema
# -----------------------------
class RegionBase(BaseModel):
    region_name: str
    description: Optional[str] = None
    is_active: bool
    is_deleted: bool

# -----------------------------
# Region Create Schema
# -----------------------------
class RegionCreate(RegionBase):
    pass

# -----------------------------
# Region Update Schema
# -----------------------------
class RegionUpdate(BaseModel):
    region_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None


    class Config:
        orm_mode = True

# -----------------------------
# Region Output Schema
# -----------------------------
class RegionOut(RegionBase):
    region_name: str
    description: Optional[str] = None
    is_active: bool
    is_deleted: bool

    class Config:
        orm_mode = True


# -----------------------------
# Paginated Response for Designation
# -----------------------------
class PaginatedRegion(BaseModel):
    items: List[RegionOut]
    total: int
    limit: int
    page: int

# -----------------------------
# Region API Response Schema
# -----------------------------
class RegionResponse(DefaultResponse):
    data: Union[RegionOut, PaginatedRegion]

    class Config:
        orm_mode = True
