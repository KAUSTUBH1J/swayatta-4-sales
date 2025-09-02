from pydantic import BaseModel
from typing import Any, Optional

class SalesResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Any] = None

    class Config:
        from_attributes = True