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

from app.auth import protected

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

@bp.get("/avatar/")
async def user_avatar(request, user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user or not user.avatar:
            return response.text("Аватар не найден", status=404)
        # Если в базе хранится MIME-тип, используйте его, иначе по умолчанию image/jpeg
        mime = getattr(user, "avatar_mime", "image/jpeg")
        return response.raw(user.avatar, content_type=mime)

# ─────────── PUT /profile (обновление профиля) ───────────

@bp.put("/profile")
@protected
async def update_profile(request):
    user_id = request.ctx.user["id"]

    # Поддержка multipart/form-data и JSON
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        form = request.form
        files = request.files
        name = form.get("name")
        surname = form.get("surname")
        patronymic = form.get("patronymic")
        phone = form.get("phone")
        email = form.get("email")
        password = form.get("password")
        avatar_file = files.get("avatar")
    else:
        data = request.json or {}
        name = data.get("name")
        surname = data.get("surname")
        patronymic = data.get("patronymic")
        phone = data.get("phone")
        email = data.get("email")
        password = data.get("password")
        avatar_file = None
        # если аватар приходит как base64-строка
        avatar_b64 = data.get("avatar")
        if avatar_b64:
            try:
                avatar_file = type("FileMock", (), {"body": base64.b64decode(avatar_b64)})()
            except Exception:
                return response.json({"error": "Invalid avatar format"}, status=400)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return response.json({"error": "User not found"}, status=404)

        if name is not None:
            user.name = name
        if surname is not None:
            user.surname = surname
        if patronymic is not None:
            user.patronymic = patronymic
        if phone is not None:
            user.phone = phone
        if email is not None:
            user.email = email
        if password:
            user.password = bcrypt.hash(password)
        if avatar_file:
            user.avatar = avatar_file.body

        await session.commit()
        return response.json({"message": "Profile updated"})

# ─────────── DELETE /profile (удаление профиля) ───────────

@bp.delete("/profile")
@protected
async def delete_profile(request):
    user_id = request.ctx.user["id"]
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return response.json({"error": "User not found"}, status=404)
        await session.delete(user)
        await session.commit()
        return response.json({"message": "User deleted"})
