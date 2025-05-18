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

api_id = 17908246
api_hash = "f338e4b3d1e23f20ead9dd68e61ebabf"
phone = "+79371842996"

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

    bot_username = '@BBTrendingBot'
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

@app.route('/auth', methods=["GET", "POST"])
def auth():
    loop = asyncio.get_event_loop()

    # Проверяем, авторизован ли уже пользователь
    if loop.run_until_complete(client.is_user_authorized()):
        return "✅ Уже авторизованы, переходите к голосованию."

    async def send_code():
        await client.connect()
        return await client.send_code_request(phone)

    async def complete_sign_in(code, password=None):
        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
            else:
                raise SessionPasswordNeededError("⚠️ Пароль нужен, но не был передан")

    try:
        if request.method == "POST":
            code = request.form.get("code")
            password = request.form.get("password")
            try:
                loop.run_until_complete(complete_sign_in(code, password))
                return "✅ Успешная авторизация!"
            except PhoneCodeInvalidError:
                return "❌ Неверный код. Попробуйте ещё раз."
            except PhoneCodeExpiredError:
                return "⌛ Код истёк. Перезапросите его через несколько минут."
            except SessionPasswordNeededError:
                # Если пароль не передан, но требуется — повторно показываем форму с сообщением
                return '''
                    <p>🔐 Требуется пароль двухфакторной аутентификации</p>
                    <form method="POST">
                        Код из Telegram: <input name="code" /><br>
                        Пароль: <input name="password" type="password" /><br>
                        <input type="submit" value="Войти" />
                    </form>
                '''

        # GET-запрос — попытка отправки кода
        try:
            loop.run_until_complete(send_code())
            msg = "📩 Код отправлен. Введите его ниже:"
        except Exception as e:
            msg = f"⚠️ Код не отправлен, возможно он уже был отправлен ранее. Просто введите его ниже: ({e})"

        return f'''
            <p>{msg}</p>
            <form method="POST">
                Введите код Telegram: <input name="code" /><br>
                Пароль (если есть): <input name="password" type="password" /><br>
                <input type="submit" value="Войти" />
            </form>
        '''

    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return f"❌ Ошибка: {e}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
