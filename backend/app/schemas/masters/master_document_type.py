from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# --------- Create ---------
class DocumentTypeCreate(BaseModel):
    document_type_name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


# --------- Update ---------
class DocumentTypeUpdate(BaseModel):
    document_type_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# --------- Response ---------
class DocumentTypeResponse(BaseModel):
    id: int
    document_type_name: str
    description: Optional[str]
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    created_by_name: Optional[str]
    updated_by_name: Optional[str]

    class Config:
        orm_mode = True
