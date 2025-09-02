from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# Base schemas for nested models
class ContactAddressBase(BaseModel):
    address_type_id: Optional[int] = None
    address: Optional[str] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    zip_code: Optional[str] = None


class ContactAddressCreate(ContactAddressBase):
    pass


class ContactAddressUpdate(ContactAddressBase):
    pass


class ContactAddressResponse(ContactAddressBase):
    id: int
    contact_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Main Contact schemas
class ContactBase(BaseModel):
    title_id: Optional[int] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    company_id: int
    designation_id: Optional[int] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    alternate_no: Optional[str] = None
    dont_solicit: bool = False
    dont_mail: bool = False
    dont_fax: bool = False
    dont_email: bool = False
    dont_call: bool = False


class ContactCreate(ContactBase):
    addresses: Optional[List[ContactAddressCreate]] = []


class ContactUpdate(ContactBase):
    addresses: Optional[List[ContactAddressUpdate]] = []


class ContactResponse(ContactBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    addresses: Optional[List[ContactAddressResponse]] = []

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True


class ContactExportOut(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    primary_no: Optional[str] = None
    company_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True