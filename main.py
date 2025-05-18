from telethon import TelegramClient
import asyncio
import os
from datetime import datetime
from flask import Flask
from threading import Thread
import nest_asyncio
import requests

nest_asyncio.apply()

# Переменные окружения
api_id = 24915095
api_hash = "abad68fdf249153b744a7bd0e6ffd528"
phone = "+79954879633"

# Инициализируем клиент Telegram
client = TelegramClient('anon', api_id, api_hash)

# Параметры голосования
vote_params = [
    'vote_-1002366046946',
]

# URL скрипта Google Apps Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxh_gh1s8ZxGzHOXCTWHUNnexw6kaAgHefPHEKo70oUGwg2F5rfO5Jy6yJyhErGqmR5/exec"

# Функция отправки POST-запроса в Google Script
def send_to_google_script(messages):
    try:
        payload = {
            "messages": messages
        }
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        print(f"[{datetime.now()}] 📬 POST в Google Script: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Google Script: {e}")

# Основная функция отправки команд
async def send_votes():
    await client.connect()

    if not await client.is_user_authorized():
        return "❌ Сессия недействительна. Загрузите корректный anon.session файл."

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
def index():
    return "🟢 Бот активен"

@app.route('/vote')
def trigger_vote():
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(send_votes())
        return result
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return f"❌ Ошибка: {str(e)}"

# Запуск Flask в отдельном потоке
def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Запускаем веб-сервер
keep_alive()
