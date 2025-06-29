from sanic import Blueprint, Request, json
from sanic.exceptions import SanicException

from app.core import security
from app.db.session import get_session
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

user_bp = Blueprint("users", url_prefix="/api/v1/users")


def _bearer_token(request: Request) -> str | None:
    auth_hdr = request.headers.get("Authorization")
    if not auth_hdr:
        return None
    parts = auth_hdr.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


@user_bp.get("/me")
async def me(request: Request):
    token = _bearer_token(request)
    if not token:
        raise SanicException("Missing bearer token", status_code=401)

    try:
        user_id = security.decode_access_token(token)
    except Exception:
        raise SanicException("Invalid or expired token", status_code=401)

    async for session in get_session():
        service = UserService(UserRepository(session))
        try:
            user = await service.get_profile(user_id)
        except ValueError:
            raise SanicException("User not found", status_code=404)
        return json(user.dict())
