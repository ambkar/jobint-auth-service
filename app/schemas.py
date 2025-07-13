from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    surname: str
    phone: str

class UserEdit(BaseModel):
    name: str = None
    surname: str = None
    avatar: str = None  # base64

class UserOut(BaseModel):
    name: str
    surname: str
    phone: str
    avatar: str = None

class CodeVerify(BaseModel):
    phone: str
    code: str

class RegisterVerify(CodeVerify):
    name: str
    surname: str
