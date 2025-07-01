import jwt
from functools import wraps
from sanic import Blueprint, response

SECRET = "732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396"

auth_bp = Blueprint("auth_guard", url_prefix="/api/v1/auth")


def check_token(request):
    hdr = request.headers.get("Authorization", "")
    if not hdr.startswith("Bearer "):
        return None
    try:
        return jwt.decode(hdr[7:], SECRET, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return None


def protected(fn):
    @wraps(fn)
    async def decorated(request, *a, **kw):
        payload = check_token(request)
        if not payload:
            return response.json({"error": "Unauthorized"}, status=401)
        request.ctx.user = payload["user"]
        return await fn(request, *a, **kw)

    return decorated


@auth_bp.get("/me")
@protected
async def me(request):
    return response.json(request.ctx.user)
