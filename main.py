from telethon import TelegramClient
import asyncio
import os
from datetime import datetime
from flask import Flask, request
from threading import Thread
import nest_asyncio
import requests
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError

nest_asyncio.apply()

api_id = 24915095
api_hash = "abad68fdf249153b744a7bd0e6ffd528"
phone = "+79954879633"

client = TelegramClient('anon', api_id, api_hash)

vote_params = [
    'vote_-1002366046946',
]

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxh_gh1s8ZxGzHOXCTWHUNnexw6kaAgHefPHEKo70oUGwg2F5rfO5Jy6yJyhErGqmR5/exec"

def send_to_google_script(messages):
    try:
        payload = {"messages": messages}
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        print(f"[{datetime.now()}] 📬 POST в Google Script: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Google Script: {e}")

async def send_votes():
    await client.connect()
    if not await client.is_user_authorized():
        return "❌ Сессия недействительна. Перейдите на /auth для входа."

    print(f"[{datetime.now()}] ✅ Авторизация успешна")

    bot_username = 'BBTrendingBot'
    messages_log = []

    for param in vote_params:
        command = f'/start {param}'
        await client.send_message(bot_username, command)
        log = f"[{datetime.now()}] 🚀 Отправлена команда: {command}"
        print(log)
        messages_log.append(log)

    await client.disconnect()
    send_to_google_script(messages_log)

    return "✅ Голосование выполнено"

# Flask-сервер
app = Flask(__name__)

@app.route('/')
