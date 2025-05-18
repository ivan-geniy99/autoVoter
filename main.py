import nest_asyncio
nest_asyncio.apply()

from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio
from datetime import datetime

app = Flask(__name__)

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

client = TelegramClient("anon", api_id, api_hash)

vote_params = ['vote_-1002366046946']
bot_username = 'BBTrendingBot'

@app.route("/")
def root():
    return f"✅ Flask работает! client = {client.is_user_authorized()}"

@app.route("/vote")
def vote():
    try:
        loop = asyncio.get_event_loop()
        if not client.is_connected():
            loop.run_until_complete(client.connect())
        authorized = loop.run_until_complete(client.is_user_authorized())
        print(f"[{datetime.now()}] Client connected: {client.is_connected()}, authorized: {authorized}")
        if not authorized:
            return "❌ Не авторизован. Нужна новая авторизация."
        result = loop.run_until_complete(send_vote())
        return result
    except Exception as e:
        return f"❌ Ошибка: {e}"

async def send_vote():
    for param in vote_params:
        await client.send_message(bot_username, f"/start {param}")
        print(f"[{datetime.now()}] ✅ Отправлена команда: /start {param}")

    # Немного подождём, чтобы бот успел ответить
    await asyncio.sleep(2)

    # Получаем последние 5 сообщений от бота
    messages = await client.get_messages(bot_username, limit=5)

    # Формируем текст сообщений
    messages_text = "\n\n".join(
        [f"[{msg.date.strftime('%Y-%m-%d %H:%M:%S')}] {msg.sender_id}: {msg.text}" for msg in messages]
    )

    print(f"[{datetime.now()}] 📨 Последние сообщения:\n{messages_text}")

    # Отправляем их в Google Apps Script
    webhook_url = "https://script.google.com/macros/s/AKfycbxh_gh1s8ZxGzHOXCTWHUNnexw6kaAgHefPHEKo70oUGwg2F5rfO5Jy6yJyhErGqmR5/exec"
    try:
        import requests
        response = requests.post(webhook_url, json={"messages": messages_text})
        print(f"[Webhook] Ответ от Google Script: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Google Script: {e}")

    return "🚀 Голос отправлен! Последние сообщения отправлены в Google Script."

if __name__ == "__main__":
    app.run(debug=True, port=5000)