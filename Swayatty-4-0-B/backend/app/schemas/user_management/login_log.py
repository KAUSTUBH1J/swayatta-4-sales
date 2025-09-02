from pydantic import BaseModel
from datetime import datetime

class LoginLogCreate(BaseModel):
    user_id: int
    login_time: datetime
    ip_address: str
    status: str
    module_id: int

class LoginLogOut(LoginLogCreate):
    id: int

    class Config:
        orm_mode = True
