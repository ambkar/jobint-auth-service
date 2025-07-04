from typing import Dict
import base64
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
    payload: Dict = {
        "user": {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "patronymic": user.patronymic,
            "phone": user.phone,
            "email": user.email,
            "avatar": base64.b64encode(user.avatar).decode() if user.avatar else None  # <--- добавляем это поле
        }
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")



# ─────────── POST /register ───────────
@bp.post("/register")
async def register(request):
    form = request.form
    files = request.files

    name = form.get("name")
    surname = form.get("surname")
    patronymic = form.get("patronymic")
    phone = form.get("phone")
    email = form.get("email")
    password = form.get("password")
    password_confirm = form.get("password_confirm")
    avatar_file = files.get("avatar")

    if not (name and surname and patronymic and phone and email and password):
        return response.json({"error": "Все поля обязательны"}, status=400)

    if password != password_confirm:
        return response.json({"error": "Пароли не совпадают"}, status=400)

    avatar_bytes = avatar_file.body if avatar_file else None

    async with AsyncSessionLocal() as session:
        # проверяем email на уникальность
        result = await session.execute(select(User).where(User.email == email))
        if result.scalars().first():
            return response.json({"error": "Пользователь с таким email уже существует"}, status=400)

        hashed_password = bcrypt.hash(password)
        new_user = User(
            name=name,
            surname=surname,
            patronymic=patronymic,
            phone=phone,
            email=email,
            password=hashed_password,
            avatar=avatar_bytes,
        )
        session.add(new_user)
        await session.commit()

        token = _token(new_user)
        return response.json({"token": token})




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
