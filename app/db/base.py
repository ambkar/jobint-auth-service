# from sqlalchemy.orm import DeclarativeBase


# class Base(DeclarativeBase):  # type: ignore[misc]
#     """Базовый класс для всех ORM-моделей."""

from sqlalchemy.ext.declarative import declarative_base  # для 1.4

Base = declarative_base()