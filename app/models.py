from sqlalchemy import Column, Integer, String, LargeBinary
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    name       = Column(String(100))
    surname    = Column(String(100))
    patronymic = Column(String(100))
    phone      = Column(String(20))
    email      = Column(String(150), unique=True, nullable=False)
    password   = Column(String(255))
    avatar     = Column(LargeBinary)
