from sqlalchemy.future import select

from app.models.user import User


class UserRepository:
    """Изолирует SQLAlchemy от сервисного слоя."""

    def __init__(self, session):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        res = await self.session.execute(select(User).where(User.id == user_id))
        return res.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(select(User).where(User.email == email))
        return res.scalars().first()

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
