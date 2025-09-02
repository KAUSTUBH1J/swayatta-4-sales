from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse


# ---------------- Base Schema ----------------
class MasterSubIndustrySegmentBase(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# ---------------- Create & Update ----------------
class MasterSubIndustrySegmentCreate(MasterSubIndustrySegmentBase):
    pass


class MasterSubIndustrySegmentUpdate(MasterSubIndustrySegmentBase):
    pass


# ---------------- Output Schema ----------------
class MasterSubIndustrySegmentOut(BaseModel):
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
class PaginatedMasterSubIndustrySegments(BaseModel):
    master_sub_industry_segments: List[MasterSubIndustrySegmentOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True


# ---------------- Export Schema ----------------
class MasterSubIndustrySegmentExportOut(BaseModel):
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
class MasterSubIndustrySegmentResponse(DefaultResponse):
    data: Optional[Union[
        MasterSubIndustrySegmentOut,
        PaginatedMasterSubIndustrySegments,
        List[MasterSubIndustrySegmentExportOut]
    ]] = None

    class Config:
        orm_mode = True
