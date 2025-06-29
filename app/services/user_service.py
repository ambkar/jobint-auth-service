from app.repositories.user_repo import UserRepository
from app.schemas.user import UserOut


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_profile(self, user_id: int) -> UserOut:
        user = await self.repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        return UserOut.from_orm(user)
