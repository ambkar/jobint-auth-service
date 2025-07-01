from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal

@asynccontextmanager
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
