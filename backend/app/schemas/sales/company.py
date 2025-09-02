from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Base schemas for nested models
class CompanyAddressBase(BaseModel):
    address_type_id: Optional[int] = None
    address: Optional[str] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    zip_code: Optional[str] = None


class CompanyAddressCreate(CompanyAddressBase):
    pass


class CompanyAddressUpdate(CompanyAddressBase):
    pass


class CompanyAddressResponse(CompanyAddressBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyTurnoverBase(BaseModel):
    year: int
    revenue: Optional[Decimal] = None
    currency_id: Optional[int] = None


class CompanyTurnoverCreate(CompanyTurnoverBase):
    pass


class CompanyTurnoverUpdate(CompanyTurnoverBase):
    pass


class CompanyTurnoverResponse(CompanyTurnoverBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyProfitBase(BaseModel):
    year: int
    revenue: Optional[Decimal] = None
    currency_id: Optional[int] = None


class CompanyProfitCreate(CompanyProfitBase):
    pass


class CompanyProfitUpdate(CompanyProfitBase):
    pass


class CompanyProfitResponse(CompanyProfitBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyDocumentBase(BaseModel):
    document_type_id: Optional[int] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None


class CompanyDocumentCreate(CompanyDocumentBase):
    pass


class CompanyDocumentUpdate(CompanyDocumentBase):
    pass


class CompanyDocumentResponse(CompanyDocumentBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Main Company schemas
class CompanyBase(BaseModel):
    gst_no: Optional[str] = None
    pan_no: Optional[str] = None
    industry_segment_id: Optional[int] = None
    company_name: str
    website: Optional[str] = None
    is_child: bool = False
    parent_company_id: Optional[int] = None
    account_type_id: Optional[int] = None
    account_sub_type_id: Optional[int] = None
    business_type_id: Optional[int] = None
    account_region_id: Optional[int] = None
    company_profile: Optional[str] = None


class CompanyCreate(CompanyBase):
    addresses: Optional[List[CompanyAddressCreate]] = []
    turnover_records: Optional[List[CompanyTurnoverCreate]] = []
    profit_records: Optional[List[CompanyProfitCreate]] = []
    documents: Optional[List[CompanyDocumentCreate]] = []


class CompanyUpdate(CompanyBase):
    addresses: Optional[List[CompanyAddressUpdate]] = []
    turnover_records: Optional[List[CompanyTurnoverUpdate]] = []
    profit_records: Optional[List[CompanyProfitUpdate]] = []
    documents: Optional[List[CompanyDocumentUpdate]] = []


class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    addresses: Optional[List[CompanyAddressResponse]] = []
    turnover_records: Optional[List[CompanyTurnoverResponse]] = []
    profit_records: Optional[List[CompanyProfitResponse]] = []
    documents: Optional[List[CompanyDocumentResponse]] = []

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True


class CompanyExportOut(BaseModel):
    id: int
    company_name: str
    gst_no: Optional[str] = None
    pan_no: Optional[str] = None
    website: Optional[str] = None
    is_child: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True