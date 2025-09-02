from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from .DefaultResponse import DefaultResponse

# ---------------- Base Schema ----------------
class ModuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False

# ---------------- Create & Update ----------------
class ModuleCreate(ModuleBase):
    created_by: Optional[int] = None

class ModuleUpdate(ModuleBase):
    updated_by: Optional[int] = None

# ---------------- Output Schema ----------------
class ModuleOut(ModuleBase):
    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True

# ---------------- Paginated List ----------------
class PaginatedModules(BaseModel):
    modules: List[ModuleOut]
    total: int
    limit: int
    page: int

    class Config:
        orm_mode = True

# ---------------- API Response ----------------
class ModuleResponse(DefaultResponse):
    data: Optional[Union[ModuleOut, PaginatedModules]] = None

    class Config:
        orm_mode = True
