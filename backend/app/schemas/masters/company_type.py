from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class CompanyTypeBase(BaseModel):
    name: str = Field(..., min_length=3)
    description : str 
    is_active: Optional[bool] = True


# ---------------- Create & Update ----------------
class CompanyTypeCreate(CompanyTypeBase):
    pass

class CompanyTypeUpdate(CompanyTypeBase):
    pass


# ---------------- Output Schema ----------------
class CompanyTypeOut(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedCompanyTypes(BaseModel):
    company_types: List[CompanyTypeOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class CompanyTypeExportOut(BaseModel):
    name: str
    is_active: Optional[bool] = True
    description : str
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class CompanyTypeResponse(DefaultResponse):
    data: Optional[Union[CompanyTypeOut, PaginatedCompanyTypes, List[CompanyTypeExportOut]]] = None

    class Config:
        orm_mode = True
