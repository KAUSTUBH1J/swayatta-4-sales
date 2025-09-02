from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union, List
from app.schemas.DefaultResponse import DefaultResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenResponse(DefaultResponse):
    data: Optional[Union[Token, List[Token]]] = None


class TokenData(BaseModel):
    user_id: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class MessageResponse(BaseModel):
    message: str

class MeResponse(BaseModel):
    email: EmailStr
