from app.core import security
from app.core.errors import DuplicateEmailError, InvalidCredentials
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import RegisterIn, LoginIn, TokenOut


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, data: RegisterIn) -> TokenOut:
        if await self.repo.get_by_email(data.email):
            raise DuplicateEmailError("Email already exists")

        user = User(
            name=data.name,
            surname=data.surname,
            patronymic=data.patronymic,
            phone=data.phone,
            email=data.email,
            password=security.hash_password(data.password),
            avatar=data.avatar,
        )
        await self.repo.add(user)
        return TokenOut(access_token=security.create_access_token(user.id))

    async def login(self, data: LoginIn) -> TokenOut:
        user = await self.repo.get_by_email(data.email)
        if not user or not security.verify_password(data.password, user.password):
            raise InvalidCredentials("Incorrect email or password")
        return TokenOut(access_token=security.create_access_token(user.id))
