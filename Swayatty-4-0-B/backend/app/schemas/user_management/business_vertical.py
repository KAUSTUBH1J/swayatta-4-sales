from pydantic import BaseModel
from typing import Optional, Union, List
from .DefaultResponse import DefaultResponse  # assuming this is defined properly
from datetime import datetime

# -----------------------------
# Base BusinessVertical Schema
# -----------------------------
class BusinessVerticalBase(BaseModel):
    business_vertical_name: str
    description: Optional[str] = None
    is_active: bool
    

# -----------------------------
# BusinessVertical Create Schema
# -----------------------------
class BusinessVerticalCreate(BusinessVerticalBase):
    pass

# -----------------------------
# BusinessVertical Update Schema
# -----------------------------
class BusinessVerticalUpdate(BaseModel):
    business_vertical_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None

    class Config:
        orm_mode = True

# -----------------------------
# BusinessVertical Output Schema
# -----------------------------
class BusinessVerticalOut(BusinessVerticalBase):
    id: int

    class Config:
        orm_mode = True

# -----------------------------
# Paginated Response for Designation
# -----------------------------
class PaginatedBusinessVertical(BaseModel):
    items: List[BusinessVerticalOut]
    total: int
    limit: int
    page: int


# -----------------------------
# BusinessVertical API Response Schema
# -----------------------------
class BusinessVerticalResponse(DefaultResponse):
    data: Union[BusinessVerticalOut, PaginatedBusinessVertical]

    class Config:
        orm_mode = True
