from sanic import Sanic, response
from sanic.request import Request
from tortoise.contrib.sanic import register_tortoise
from models import User, TempCode
from db import init_db
from telegram_sender import generate_code, send_code_via_telegram
from utils import clear_expired_codes
import asyncio

app = Sanic("AuthService")

@app.listener('before_server_start')
async def setup_db(app, loop):
    await init_db()

@app.post("/auth/send_code")
async def send_code(request: Request):
    data = request.json
    phone = data.get("phone")
    code = generate_code()
    await TempCode.create(phone=phone, code=code)
    asyncio.create_task(send_code_via_telegram(phone, code))
    return response.json({"status": "code_sent"})

@app.post("/auth/verify_code")
async def verify_code(request: Request):
    data = request.json
    phone = data.get("phone")
    code = data.get("code")
    temp_code = await TempCode.filter(phone=phone, code=code).first()
    if temp_code:
        await TempCode.filter(phone=phone).delete()
        user = await User.filter(phone=phone).first()
        if not user:
            user = await User.create(phone=phone)
        # Здесь можно создать и вернуть токен
        return response.json({"status": "ok", "user_id": user.id})
    return response.json({"status": "invalid_code"}, status=400)

@app.post("/auth/register")
async def register(request: Request):
    data = request.json
    phone = data.get("phone")
    name = data.get("name")
    surname = data.get("surname")
    avatar = data.get("avatar")  # base64
    user = await User.filter(phone=phone).first()
    if user:
        return response.json({"status": "user_exists"}, status=400)
    user = await User.create(phone=phone, name=name, surname=surname, avatar=avatar)
    return response.json({"status": "registered", "user_id": user.id})

@app.post("/auth/login")
async def login(request: Request):
    data = request.json
    phone = data.get("phone")
    user = await User.filter(phone=phone).first()
    if user:
        return response.json({"status": "ok", "user_id": user.id})
    return response.json({"status": "not_found"}, status=404)

@app.put("/auth/profile")
async def update_profile(request: Request):
    data = request.json
    user_id = data.get("user_id")
    user = await User.filter(id=user_id).first()
    if not user:
        return response.json({"status": "not_found"}, status=404)
    user.name = data.get("name", user.name)
    user.surname = data.get("surname", user.surname)
    user.avatar = data.get("avatar", user.avatar)
    await user.save()
    return response.json({"status": "updated"})

@app.delete("/auth/delete")
async def delete_account(request: Request):
    data = request.json
    user_id = data.get("user_id")
    await User.filter(id=user_id).delete()
    return response.json({"status": "deleted"})

@app.post("/auth/logout")
async def logout(request: Request):
    # Здесь можно реализовать логику удаления токена/сессии
    return response.json({"status": "logged_out"})

@app.middleware('response')
async def cleanup_temp_codes(request, response):
    await clear_expired_codes()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
