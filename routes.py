# routes.py
import jwt
from passlib.hash import bcrypt
from sanic import Blueprint, response
from sqlalchemy.future import select
from database import AsyncSessionLocal
from models import User
from auth import SECRET

bp = Blueprint("auth_api", url_prefix="/api/v1/auth")


def _gen_token(user: User) -> str:
    payload = {
        "user": {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "patronymic": user.patronymic,
            "phone": user.phone,
            "email": user.email,
        }
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


@bp.post("/register")
async def register(request):
    data = request.json or {}
    mandatory = ("name", "surname", "patronymic", "phone", "email", "password")
    if any(k not in data or not data[k] for k in mandatory):
        return response.json({"error": "Все поля обязательны"}, status=400)

    async with AsyncSessionLocal() as session:
        dup = await session.execute(select(User).where(User.email == data["email"]))
        if dup.scalars().first():
            return response.json({"error": "Email уже зарегистрирован"}, status=409)

        user = User(
            name=data["name"],
            surname=data["surname"],
            patronymic=data["patronymic"],
            phone=data["phone"],
            email=data["email"],
            password=bcrypt.hash(data["password"]),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return response.json({"token": _gen_token(user)}, status=201)


@bp.post("/login")
async def login(request):
    data = request.json or {}
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.email == data.get("email")))
        user = res.scalars().first()

    if not user or not bcrypt.verify(data.get("password", ""), user.password):
        return response.json({"error": "Неверный email или пароль"}, status=401)

    return response.json({"token": _gen_token(user)})
