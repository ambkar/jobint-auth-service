from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)
    patronymic: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    email: EmailStr
    password: str = Field(min_length=8)
    avatar: Optional[str] = Field(
        default=None,
        description="Base64-encoded avatar image"
    )

class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    token: str
