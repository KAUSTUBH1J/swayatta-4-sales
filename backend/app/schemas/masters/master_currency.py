from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


# --------- Base ---------
class MasterCurrencyBase(BaseModel):
    currency_code: str = Field(..., min_length=2, max_length=10)
    currency_name: str = Field(..., min_length=2, max_length=50)
    symbol: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# --------- Create ---------
class MasterCurrencyCreate(MasterCurrencyBase):
    pass


# --------- Update ---------
class MasterCurrencyUpdate(BaseModel):
    currency_code: Optional[str] = None
    currency_name: Optional[str] = None
    symbol: Optional[str] = None
    is_active: Optional[bool] = None


# --------- Output ---------
class MasterCurrencyOut(BaseModel):
    currency_id: int
    currency_code: str
    currency_name: str
    symbol: Optional[str]
    is_active: bool
    is_deleted: bool
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True


# --------- Paginated ---------
class PaginatedMasterCurrencies(BaseModel):
    currencies: List[MasterCurrencyOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True
