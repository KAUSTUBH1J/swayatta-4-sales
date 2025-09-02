from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class SubDepartmentBase(BaseModel):
    name: str = Field(..., min_length=2)
    code: Optional[str] = None
    department_id: int
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class SubDepartmentCreate(SubDepartmentBase):
    pass

class SubDepartmentUpdate(SubDepartmentBase):
    pass


# ---------------- Output Schema ----------------
class SubDepartmentOut(BaseModel):
    id: int
    name: Optional[str] = None
    code: Optional[str] = None
    department_id: int
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Foreign key display names
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    department_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class SubDepartmentExportOut(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    department_name: Optional[str] = None
    is_active: Optional[bool] = True

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- Paginated List ----------------
class PaginatedSubDepartments(BaseModel):
    sub_departments: List[SubDepartmentOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class SubDepartmentResponse(DefaultResponse):
    data: Optional[Union[
        SubDepartmentOut, 
        PaginatedSubDepartments, 
        List[SubDepartmentExportOut]
    ]] = None

    class Config:
        orm_mode = True
