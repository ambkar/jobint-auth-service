from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://jobint_user:Karen_2003@db:5432/jobint")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

# Функция для создания всех таблиц из моделей
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Если файл запускается как скрипт, создать все таблицы
if __name__ == "__main__":
    asyncio.run(create_tables())
