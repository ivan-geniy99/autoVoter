from flask import Flask
from telethon import TelegramClient
import os
import asyncio
from datetime import datetime

app = Flask(__name__)

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
phone = os.environ.get("PHONE")

client = TelegramClient("anon", api_id, api_hash)

vote_params = ['vote_-1002366046946']
bot_username = 'BBTrendingBot'

@app.route("/")
def root():
    return "✅ Flask работает!"

@app.route("/vote")
def vote():
    asyncio.run(send_vote())
    return "🚀 Голос отправлен!"

async def send_vote():
    if not client.is_connected():
        await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        print("⚠️ Требуется авторизация. Это не сработает автоматически.")
        return

    for param in vote_params:
        await client.send_message(bot_username, f"/start {param}")
        print(f"[{datetime.now()}] ✅ Отправлена команда: /start {param}")
