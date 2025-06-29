from sanic import Blueprint, Request, json
from sanic.exceptions import SanicException

from app.db.session import get_session
from app.repositories.user_repo import UserRepository
from app.schemas.auth import RegisterIn, LoginIn
from app.services.auth_service import AuthService
from app.core.errors import DuplicateEmailError, InvalidCredentials

auth_bp = Blueprint("auth", url_prefix="/api/v1/auth")


@auth_bp.post("/register")
async def register(request: Request):
    data = RegisterIn(**request.json)

    async for session in get_session():
        service = AuthService(UserRepository(session))
        try:
            token = await service.register(data)
        except DuplicateEmailError as exc:
            raise SanicException(str(exc), status_code=409)
        return json(token.dict(), status=201)


@auth_bp.post("/login")
async def login(request: Request):
    data = LoginIn(**request.json)

    async for session in get_session():
        service = AuthService(UserRepository(session))
        try:
            token = await service.login(data)
        except InvalidCredentials as exc:
            raise SanicException(str(exc), status_code=401)
        return json(token.dict())
