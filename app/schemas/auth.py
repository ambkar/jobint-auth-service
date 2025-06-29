from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str
    surname: str
    patronymic: str | None = None
    phone: str | None = None
    email: EmailStr
    password: str = Field(min_length=8)
    avatar: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
