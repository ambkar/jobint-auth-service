from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):  # type: ignore[misc]
    """Базовый класс для всех ORM-моделей."""
