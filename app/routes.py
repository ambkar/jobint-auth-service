import jwt
from passlib.hash import bcrypt
from sanic import Blueprint, response
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User
from app.auth import SECRET

bp = Blueprint("auth_api", url_prefix="/api/v1/auth")


def _token(user: User) -> str:
    data = {"user": {k: getattr(user, k) for k in
                     ("id", "name", "surname", "patronymic", "phone", "email")}}
    return jwt.encode(data, SECRET, algorithm="HS256")


@bp.post("/register")
async def register(request):
    data = request.json or {}
    required = ("name", "surname", "patronymic", "phone", "email", "password")
    if any(not data.get(k) for k in required):
        return response.json({"error": "Все поля обязательны"}, status=400)

    async with AsyncSessionLocal() as ses:
        if (await ses.execute(select(User).where(User.email == data["email"]))).scalar():
            return response.json({"error": "Email уже зарегистрирован"}, status=409)
        user = User(**{k: data[k] for k in required if k != "password"},
                    password=bcrypt.hash(data["password"]))
        ses.add(user)
        await ses.commit()
        await ses.refresh(user)

    return response.json({"token": _token(user)}, status=201)


@bp.post("/login")
async def login(request):
    data = request.json or {}
    async with AsyncSessionLocal() as ses:
        res = await ses.execute(select(User).where(User.email == data.get("email")))
        user = res.scalar()
    if not user or not bcrypt.verify(data.get("password", ""), user.password):
        return response.json({"error": "Неверный email или пароль"}, status=401)
    return response.json({"token": _token(user)})
