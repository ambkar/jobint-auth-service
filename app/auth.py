import random
import string
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

API_ID = '27195769'
API_HASH = '1b917b5d0750d0425c71a95ba92e736a'
TG_PHONE = '+79682726227'

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_code_via_telegram(phone, code):
    client = TelegramClient('anon', API_ID, API_HASH)
    client.start(phone=TG_PHONE)
    contact = InputPhoneContact(client_id=0, phone=phone, first_name='', last_name='')
    result = client(ImportContactsRequest([contact]))
    user = result.users[0] if result.users else None
    if user:
        client.send_message(user.id, f"Ваш код: {code}")
    client.disconnect()
