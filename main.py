from telethon import TelegramClient
import asyncio
import os
from datetime import datetime
from flask import Flask
from threading import Thread

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

# Основная функция отправки команд
async def send_votes():
    if not client.is_connected():
        await client.connect()
        if not await client.is_user_authorized():
            await client.start(phone)
    print(f"[{datetime.now()}] ✅ Авторизация успешна")

    bot_username = 'BBTrendingBot'

    for param in vote_params:
        await client.send_message(bot_username, f'/start {param}')
        print(f"[{datetime.now()}] 🚀 Отправлена команда: /start {param}")

    await client.disconnect()
    return "✅ Голосование выполнено"

# Flask-сервер
app = Flask('')

@app.route('/')
def index():
    return "🟢 Бот активен"

@app.route('/vote')
def trigger_vote():
    try:
        asyncio.run(send_votes())
        return "✅ Голосование отправлено"
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
