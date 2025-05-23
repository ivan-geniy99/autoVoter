from telethon import TelegramClient
import asyncio
import os
from datetime import datetime
from flask import Flask, request
from threading import Thread
import nest_asyncio
import requests
import subprocess
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

def git_commit_and_push_session():
    try:
        subprocess.run(['git', 'add', 'anon.session'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Обновлена сессия после /auth'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("✅ anon.session успешно запушен в репозиторий")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка git: {e}")

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

    async def check_authorized():
        await client.connect()
        authorized = await client.is_user_authorized()
        await client.disconnect()
        return authorized

    async def send_code():
        await client.connect()
        return await client.send_code_request(phone)

    async def complete_sign_in(code, password=None):
        await client.connect()
        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
            else:
                raise SessionPasswordNeededError("⚠️ Пароль нужен, но не был передан")
        finally:
            await client.disconnect()

        # После успешной авторизации пушим сессию
        git_commit_and_push_session()

    try:
        # Сначала проверяем авторизацию с подключением
        if loop.run_until_complete(check_authorized()):
            return "✅ Уже авторизованы, переходите к голосованию."

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
                return '''
                    <p>🔐 Требуется пароль двухфакторной аутентификации</p>
                    <form method="POST">
                        Код из Telegram: <input name="code" /><br>
                        Пароль: <input name="password" type="password" /><br>
                        <input type="submit" value="Войти" />
                    </form>
                '''

        # GET-запрос — отправляем код
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
