import json
import re
from pathlib import Path

from aiogram_dialog import DialogManager
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from telethon import TelegramClient

from bot.database.queries import get_formatted_chats_list, db_get_chat, db_change_chat
from bot.dialogs.states_groups import MainDialog
from bot.telethon.telethon_manager import check_proxy_validity


# Вывод списка ботоа
async def userbots_main_getter(**kwargs):
    # Путь к папке с сессиями
    sessions_dir = Path("bot/pyrogram/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)  # Создаём папку если её нет

    # Получаем и сортируем список .session файлов
    session_files = sorted(
        file.name for file in sessions_dir.glob("*.session") if file.is_file()
    )

    # Форматируем список с нумерацией и HTML-разметкой
    formatted_sessions = "\n".join(
        f"{i + 1}) <code>{name}</code> - готов ✅"
        for i, name in enumerate(session_files)
    )

    return {'session_list': formatted_sessions}



# Вывод краткой актуальной информации о чатах из БД
async def main_menu_getter(dialog_manager: DialogManager, **kwargs):
    bot = dialog_manager.event.bot
    chat_status_list = await get_formatted_chats_list()

    # Получаем все чаты из БД
    chats = await db_get_chat()
    if chats:
        for chat in chats:
            try:
                # Получаем актуальную информацию о чате из Telegram
                tg_chat = await bot.get_chat(chat['id'])
                if tg_chat.title != chat['title']:
                    # Если название изменилось, обновляем в БД
                    await db_change_chat(chat['username'], {'title': tg_chat.title})
            except Exception as e:
                print(f"Ошибка при обновлении title чата {chat['username']}: {e}")

    chat_status_list = '\n\n'.join(chat_status_list)
    return {"chat_status_list": chat_status_list}


# Вывод полной информации о чате
async def chat_info_getter(dialog_manager: DialogManager, **kwargs):
    username = dialog_manager.dialog_data.get('chat_settings_username')
    chat = await db_get_chat(username)

    if chat:
        return chat
    else:
        await dialog_manager.event.answer(f'f"Ошибка при получении чата @{username}')
        await dialog_manager.switch_to(MainDialog.main_menu)


# Конвертация telethon сессии в pyrogram сессию
async def convert_telethon_to_pyrogram(dialog_manager: DialogManager) -> dict:
    print("[1/5] Начало конвертации Telethon → Pyrogram")

    # Получаем пути и данные
    telethon_session_path = dialog_manager.dialog_data.get('add_bot_session_path')
    telethon_json_path = dialog_manager.dialog_data.get('add_bot_json_path')
    proxy_dict = dialog_manager.dialog_data.get('add_bot_proxy_dict')

    # Проверяем прокси
    print("[2/5] Проверка валидности прокси...")
    proxy_check = await check_proxy_validity(proxy_dict)
    if not proxy_check["result"]:
        return proxy_check

    # Загружаем JSON данные
    try:
        with open(telethon_json_path, 'r') as f:
            json_data = json.load(f)
        print(f"[3/5] JSON успешно загружен (app_id: {json_data['app_id']}, phone: {json_data['phone']})")
    except Exception as e:
        return {"result": False, "result_text": f"❌ Ошибка загрузки JSON: {str(e)}"}

    # Проверяем сессию Telethon
    print("[4/5] Проверка Telethon сессии...")
    try:
        telethon_client = TelegramClient(
            telethon_session_path,
            api_id=int(json_data['app_id']),
            api_hash=json_data['app_hash'],
        )

        async with telethon_client:
            if not await telethon_client.is_user_authorized():
                return {"result": False, "result_text": "❌ Telethon сессия невалидна"}

            me = await telethon_client.get_me()
            account_info = {
                "phone": json_data['phone'],
                "first_name": me.first_name,
                "username": me.username
            }
            print(f"Telethon сессия валидна (user: {me.first_name or 'None'} @{me.username or 'None'})")
    except Exception as e:
        return {"result": False, "result_text": f"❌ Ошибка проверки Telethon: {str(e)}"}

    # Создаем Pyrogram сессию
    pyrogram_session_path = Path("bot/pyrogram/sessions") / Path(telethon_session_path).stem
    userbot = None

    try:
        print("[5/5] Создание Pyrogram сессии...")
        userbot = Client(
            name=str(pyrogram_session_path),
            api_id=json_data['app_id'],
            api_hash=json_data['app_hash'],
            phone_number=json_data['phone'],
        )

        await userbot.connect()
        send_code_data = await userbot.send_code(json_data['phone'])
        phone_code_hash = send_code_data.phone_code_hash

        async with telethon_client:
            msg_from_telegram = await telethon_client.get_messages(777000, limit=1)
            msg_text = msg_from_telegram[0].message
            code_in_msg = re.search(r'\d+', msg_text)

            if not code_in_msg:
                return {"result": False, "result_text": "❌ Не удалось получить код из Telegram"}

            phone_code = code_in_msg.group()
            print(f"Получен код подтверждения: {phone_code}")

        # Пытаемся войти в аккаунт
        try:
            # Обычный вход
            await userbot.sign_in(
                phone_number=json_data['phone'],
                phone_code_hash=phone_code_hash,
                phone_code=phone_code
            )
        except SessionPasswordNeeded:
            # Если требуется 2FA
            if 'twoFA' not in json_data:
                return {"result": False, "result_text": "❌ Требуется 2FA пароль, но он не указан в JSON"}

            try:
                await userbot.check_password(json_data['twoFA'])
            except Exception as e:
                return {"result": False, "result_text": f"❌ Ошибка ввода 2FA пароля: {str(e)}"}

        # Получаем информацию о пользователе
        pyrogram_me = await userbot.get_me()

        return {
            "result": True,
            "result_text": (
                f"✅ Аккаунт успешно подключен!\n\n"
                f"📱 Телефон: +{json_data['phone']}\n"
                f"👤 Имя: {pyrogram_me.first_name or 'Нет'}\n"
                f"🔗 Username: @{pyrogram_me.username or 'Нет'}\n\n"
                f"<code>Pyrogram сессия сохранена: {pyrogram_session_path}.session</code>"
            ),
            "account_info": account_info
        }

    except Exception as e:
        return {"result": False, "result_text": f"❌ Ошибка создания Pyrogram сессии: {str(e)}"}
    finally:
        if userbot:
            try:
                await userbot.disconnect()
            except:
                pass


async def add_bot_result_getter(dialog_manager: DialogManager, **kwargs):
    result = await convert_telethon_to_pyrogram(dialog_manager)
    return result