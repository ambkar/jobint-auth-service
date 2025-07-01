from typing import Dict

import jwt
from passlib.hash import bcrypt
from sanic import Blueprint, response
from sanic_ext import validate, openapi
from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models import User
from app.schemas import RegisterIn, LoginIn, TokenOut

# JWT–секрет хранится пока в коде; в проде вынесите в переменную окружения
SECRET = "732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396"

bp = Blueprint("auth_api", url_prefix="/api/v1/auth")


# ─────────── helpers ───────────
def _token(user: User) -> str:
    """Собираем JWT-пейлоад и подписываем."""
    payload: Dict = {
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


# ─────────── POST /register ───────────
@bp.post("/register")
@validate(json=RegisterIn)                # валидация + описание body
@openapi.response(201, TokenOut)          # схема успешного ответа
async def register(request, body: RegisterIn):   # body типизирован схемой
    data = body.model_dump()

    async with AsyncSessionLocal() as session:
        # проверяем дубликат
        exists = await session.execute(select(User).where(User.email == data["email"]))
        if exists.scalars().first():
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

    return response.json({"token": _token(user)}, status=201)


# ─────────── POST /login ───────────
@bp.post("/login")
@validate(json=LoginIn)
@openapi.response(200, TokenOut)
async def login(request, body: LoginIn):
    data = body.model_dump()

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.email == data["email"]))
        user = res.scalars().first()

    if not user or not bcrypt.verify(data["password"], user.password):
        return response.json({"error": "Неверный email или пароль"}, status=401)

    return response.json({"token": _token(user)})
