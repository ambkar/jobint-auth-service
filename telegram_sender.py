import random
import string
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import os

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
TG_PHONE = os.getenv('TG_PHONE')

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

async def send_code_via_telegram(phone, code):
    async with TelegramClient('anon', API_ID, API_HASH) as client:
        await client.start(phone=TG_PHONE)
        contact = InputPhoneContact(client_id=0, phone=phone, first_name='', last_name='')
        result = await client(ImportContactsRequest([contact]))
        user = result.users[0] if result.users else None
        if user:
            await client.send_message(user.id, f"Ваш код: {code}")
