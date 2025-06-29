from pydantic import BaseModel, EmailStr, ConfigDict


class UserOut(BaseModel):
    id: int
    name: str
    surname: str | None = None
    patronymic: str | None = None
    phone: str | None = None
    email: EmailStr
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)