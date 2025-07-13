from sqlalchemy import Column, Integer, String, LargeBinary
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    surname = Column(String(100))
    phone = Column(String(20), unique=True, nullable=False)
    avatar = Column(LargeBinary, nullable=True)
