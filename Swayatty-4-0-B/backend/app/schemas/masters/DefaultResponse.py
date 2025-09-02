from pydantic import BaseModel
from typing import List, Optional, Any, Union


class DefaultResponse(BaseModel):
    status_code: Union[str, int]
    message: str
    data: Optional[Any]
