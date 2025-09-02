from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema (Request Validation) ----------------
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=3)
    username: str = Field(
        ..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_.-]+$"
    )
    email: EmailStr
    contact_no: Optional[str] = Field(default=None, pattern="^[0-9]{10,13}$")
    gender: Optional[str] = Field(default=None, description="Male / Female / Other")
    dob: Optional[datetime] = None
    profile_photo: Optional[str] = None

    department_id: Optional[int] = None
    sub_department_id: Optional[int] = None
    designation_id: Optional[int] = None
    is_reporting: Optional[bool] = False
    reporting_to: Optional[int] = None
    region_id: Optional[int] = None
    role_id: Optional[int] = None
    assign_modules: Optional[str] = None
    address: Optional[str] = None
    business_vertical_id: Optional[int] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


# ---------------- Output Schema (Response Only, All Optional) ----------------
class UserOut(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    contact_no: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    profile_photo: Optional[str] = None
    department_id: Optional[int] = None
    sub_department_id: Optional[int] = None
    designation_id: Optional[int] = None
    is_reporting: Optional[bool] = None
    reporting_to: Optional[int] = None
    region_id: Optional[int] = None
    role_id: Optional[int] = None
    assign_modules: Optional[str] = None
    address: Optional[str] = None
    business_vertical_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Foreign key names
    department_name: Optional[str] = None
    sub_department_name: Optional[str] = None
    designation_name: Optional[str] = None
    region_name: Optional[str] = None
    role_name: Optional[str] = None
    business_vertical_name: Optional[str] = None
    manager_name: Optional[str] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------- Paginated ----------------
class PaginatedUsers(BaseModel):
    users: List[UserOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------- User Export Schema ------------------
class UserExportOut(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    contact_no: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    department_name: Optional[str] = None
    sub_department_name: Optional[str] = None
    designation_name: Optional[str] = None
    role_name: Optional[str] = None
    region_name: Optional[str] = None
    business_vertical_name: Optional[str] = None
    manager_name: Optional[str] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ---------------- API Response ----------------
class UserResponse(DefaultResponse):
    data: Optional[Union[UserOut, PaginatedUsers]] = None

    class Config:
        orm_mode = True
