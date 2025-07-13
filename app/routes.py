from flask import Blueprint, request, jsonify, session
from sqlalchemy.future import select
from sqlalchemy import delete
from .database import AsyncSessionLocal
from .models import User
from .auth import generate_code, send_code_via_telegram

bp = Blueprint('routes', __name__)

@bp.route('/api/register', methods=['POST'])
async def register():
    data = request.json
    phone = data['phone']
    code = generate_code()
    session['reg_code'] = code
    session['reg_phone'] = phone
    await send_code_via_telegram(phone, code)
    return jsonify({'status': 'code_sent'})

@bp.route('/api/verify', methods=['POST'])
async def verify():
    data = request.json
    code = data['code']
    name = data.get('name', '')
    surname = data.get('surname', '')
    phone = session.get('reg_phone')
    if code != session.get('reg_code'):
        return jsonify({'status': 'error', 'msg': 'Неверный код'}), 400
    async with AsyncSessionLocal() as db:
        user = User(name=name, surname=surname, phone=phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        session['user_id'] = user.id
    return jsonify({'status': 'ok'})

@bp.route('/api/login', methods=['POST'])
async def login():
    data = request.json
    phone = data['phone']
    code = generate_code()
    session['login_code'] = code
    session['login_phone'] = phone
    await send_code_via_telegram(phone, code)
    return jsonify({'status': 'code_sent'})

@bp.route('/api/login-verify', methods=['POST'])
async def login_verify():
    data = request.json
    code = data['code']
    phone = session.get('login_phone')
    if code != session.get('login_code'):
        return jsonify({'status': 'error', 'msg': 'Неверный код'}), 400
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar()
        if not user:
            return jsonify({'status': 'error', 'msg': 'Пользователь не найден'}), 404
        session['user_id'] = user.id
    return jsonify({'status': 'ok'})

@bp.route('/api/profile', methods=['GET'])
async def profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'unauthorized'}), 401
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar()
        if not user:
            return jsonify({'status': 'not found'}), 404
        return jsonify({
            'name': user.name,
            'surname': user.surname,
            'phone': user.phone,
            'avatar': user.avatar.decode() if user.avatar else None
        })

@bp.route('/api/profile', methods=['POST'])
async def profile_edit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'unauthorized'}), 401
    data = request.json
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar()
        if not user:
            return jsonify({'status': 'not found'}), 404
        user.name = data.get('name', user.name)
        user.surname = data.get('surname', user.surname)
        user.avatar = data.get('avatar', user.avatar)
        await db.commit()
    return jsonify({'status': 'ok'})

@bp.route('/api/delete', methods=['POST'])
async def delete():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'unauthorized'}), 401
    async with AsyncSessionLocal() as db:
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
    session.clear()
    return jsonify({'status': 'deleted'})

@bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'ok'})
