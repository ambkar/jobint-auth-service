from functools import wraps
import jwt
from sanic import response, Blueprint

auth_bp = Blueprint("auth_extra", url_prefix="api/v1/auth")

def check_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, request.app.config.SECRET, algorithms=["HS256"])
        request.ctx.user = payload.get("user")
        return True
    except jwt.exceptions.InvalidTokenError:
        return False

def protected(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        if check_token(request):
            return await f(request, *args, **kwargs)
        else:
            return response.json({"error": "Unauthorized"}, status=401)
    return decorated_function

@auth_bp.get("/me")
@protected
async def me(request):
    return response.json({"user": request.ctx.user})
