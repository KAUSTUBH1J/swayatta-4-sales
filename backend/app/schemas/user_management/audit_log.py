from pydantic import BaseModel
from datetime import datetime

class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    table_name: str
    timestamp: datetime
    module_id: int

class AuditLogOut(AuditLogCreate):
    id: int

    class Config:
        orm_mode = True
