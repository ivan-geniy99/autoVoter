from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio
from datetime import datetime
import nest_asyncio

nest_asyncio.apply()  # Важная строчка — позволяет переиспользовать event loop

app = Flask(__name__)

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_str = os.environ.get("SESSION_STRING")

client = TelegramClient(StringSession(session_str), api_id, api_hash)

vote_params = ['vote_-1002366046946']
bot_username = 'BBTrendingBot'

@app.before_first_request
def startup():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.connect())

@app.route("/")
def root():
    return "✅ Flask работает!"

@app.route("/vote")
def vote():
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(send_vote())
        return result
    except Exception as e:
        return f"❌ Ошибка: {e}"

async def send_vote():
    if not await client.is_user_authorized():
        return "❌ Не авторизован. Нужна новая авторизация."
    
    for param in vote_params:
        await client.send_message(bot_username, f"/start {param}")
        print(f"[{datetime.now()}] ✅ Отправлена команда: /start {param}")
    
    return "🚀 Голос отправлен!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
