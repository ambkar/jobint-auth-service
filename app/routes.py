from flask import Blueprint, request, jsonify, session
from sqlalchemy.future import select
from sqlalchemy import delete
from datetime import datetime, timedelta
from .database import AsyncSessionLocal
from .models import User, ConfirmationCode
from .auth import generate_code, send_code_via_telegram
from .schemas import RegisterVerify, CodeVerify
from pydantic import ValidationError

bp = Blueprint('routes', __name__)

@bp.route('/api/register', methods=['POST'])
async def register():
    data = request.json
    phone = data['phone']
    code = generate_code()
    async with AsyncSessionLocal() as db:
        conf_code = ConfirmationCode(phone=phone, code=code, purpose='register')
        db.add(conf_code)
        await db.commit()
    await send_code_via_telegram(phone, code)
    return jsonify({'status': 'code_sent'})

@bp.route('/api/verify', methods=['POST'])
async def verify():
    try:
        data = RegisterVerify(**request.json)
    except ValidationError as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 400

    phone = data.phone
    code = data.code
    name = data.name
    surname = data.surname

    async with AsyncSessionLocal() as db:
        ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
        result = await db.execute(
            select(ConfirmationCode)
            .where(
                ConfirmationCode.phone == phone,
                ConfirmationCode.code == code,
                ConfirmationCode.purpose == 'register',
                ConfirmationCode.created_at > ten_min_ago
            )
        )
        conf_code = result.scalar()
        if not conf_code:
            return jsonify({'status': 'error', 'msg': 'Неверный код'}), 400
        await db.delete(conf_code)
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
    async with AsyncSessionLocal() as db:
        conf_code = ConfirmationCode(phone=phone, code=code, purpose='login')
        db.add(conf_code)
        await db.commit()
    await send_code_via_telegram(phone, code)
    return jsonify({'status': 'code_sent'})

@bp.route('/api/login-verify', methods=['POST'])
async def login_verify():
    try:
        data = CodeVerify(**request.json)
    except ValidationError as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 400

    phone = data.phone
    code = data.code

    async with AsyncSessionLocal() as db:
        ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
        result = await db.execute(
            select(ConfirmationCode)
            .where(
                ConfirmationCode.phone == phone,
                ConfirmationCode.code == code,
                ConfirmationCode.purpose == 'login',
                ConfirmationCode.created_at > ten_min_ago
            )
        )
        conf_code = result.scalar()
        if not conf_code:
            return jsonify({'status': 'error', 'msg': 'Неверный код'}), 400
        await db.delete(conf_code)
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
