from flask import Flask
from telethon import TelegramClient
import os
import asyncio
import nest_asyncio
from datetime import datetime

nest_asyncio.apply()

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
    result = asyncio.run(send_vote())
    return result

async def send_vote():
    await client.connect()
    if not await client.is_user_authorized():
        return "❌ Не авторизован. Нужна ручная авторизация."
    
    for param in vote_params:
        await client.send_message(bot_username, f"/start {param}")
        print(f"[{datetime.now()}] ✅ Отправлена команда: /start {param}")
    
    return "🚀 Голос отправлен!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
