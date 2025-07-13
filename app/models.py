from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    surname = Column(String(100))
    phone = Column(String(20), unique=True, nullable=False)
    avatar = Column(LargeBinary, nullable=True)

class ConfirmationCode(Base):
    __tablename__ = "confirmation_codes"
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    purpose = Column(String(20), nullable=False)
