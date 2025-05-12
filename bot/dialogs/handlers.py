from pathlib import Path

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.input import MessageInput

from bot.database.queries import db_change_all_chats_status, db_delete_chat, db_add_chat, db_change_chat
from bot.dialogs.states_groups import MainDialog, AddUserbot


# Запуск/остановка работы ботов во всех чатах
async def change_all_chats_status(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    # Определяем действие (запуск/остановка) по callback.data
    action = callback.data
    new_status = action == 'all_start'  # True для запуска, False для остановки

    try:
        # Вызываем функцию обновления статуса в БД
        success = await db_change_all_chats_status(new_status)

        if success:
            # Формируем сообщение об успехе
            status_msg = ("Все чаты успешно запущены" if new_status else "Все чаты успешно остановлены")
            await callback.answer(status_msg)
        else:
            await callback.answer("Не удалось изменить статус чатов",)

    except Exception as e:
        print(f"Ошибка при изменении статуса чатов: {e}")
        await callback.answer("Произошла ошибка при изменении статуса",)
    finally:
        # Обновляем интерфейс после изменения
        await dialog_manager.show()


# Запуск/остановка работы ботов в чате
async def change_chat_status(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    # Определяем действие (запуск/остановка) по callback.data
    action = callback.data
    new_status = action == 'chat_start'  # True для запуска, False для остановки

    try:
        # Вызываем функцию обновления статуса в БД
        username = dialog_manager.dialog_data.get('chat_settings_username')
        await db_change_chat(username, {'status': new_status})
    except Exception as e:
        print(f"Ошибка при изменении статуса чатов: {e}")
        await callback.answer("Произошла ошибка при изменении статуса",)
    finally:
        # Обновляем интерфейс после изменения
        await dialog_manager.show()


# Сменить режим работы ботов в чате
async def change_chat_mode(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    # Определяем режима (Диалог/Вопрос) по callback.data
    action = callback.data
    new_mode = 'Диалог' if action == 'dialog_mode' else 'Вопрос'  # True для запуска, False для остановки

    try:
        # Вызываем функцию обновления статуса в БД
        username = dialog_manager.dialog_data.get('chat_settings_username')
        await db_change_chat(username, {'work_mode': new_mode})

    except Exception as e:
        print(f"Ошибка при изменении режима работы чата: {e}")
        await callback.answer("Произошла ошибка при изменении статуса",)
    finally:
        # Обновляем интерфейс после изменения
        await dialog_manager.show()


# Удалить чат
async def delete_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Извлекаем username из разных форматов
    if message.text.startswith('https://t.me/'):
        chat_username = message.text.split('/')[-1]
    else:
        chat_username = message.text.replace('@', '')

    # Удаляем чат из БЗ
    result = await db_delete_chat(chat_username)

    # Оповещаем пользователя
    await dialog_manager.event.answer(
        f"Чат @{chat_username} успешно удален" if result else f"Чат @{chat_username} не найден"
    )

    # Обновляем диалог
    await dialog_manager.switch_to(state=MainDialog.main_menu)


# Добавить чат
async def add_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Извлекаем username из разных форматов
    if message.text.startswith('https://t.me/'):
        chat_identifier = message.text.split('/')[-1]
    else:
        chat_identifier = message.text.replace('@', '')

    telegram_chat = await dialog_manager.event.bot.get_chat("@" + chat_identifier)

    # Если чат не найден
    if not telegram_chat:
        await dialog_manager.event.answer(f"Чат {chat_identifier} не найден")
        await dialog_manager.switch_to(state=MainDialog.main_menu)
        return

    # Добавляем чат в БД
    result = await db_add_chat(telegram_chat)

    # Оповещаем пользователя и обновляем диалог
    await dialog_manager.event.answer(
        f"Чат @{telegram_chat.username} успешно добавлен" if result else f"{chat_identifier} - ошибка базы данных"
    )
    await dialog_manager.switch_to(state=MainDialog.main_menu)


# Изменить настройки чата
async def settings_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Извлекаем username из разных форматов
    if message.text.startswith('https://t.me/'):
        chat_username = message.text.split('/')[-1]
    else:
        chat_username = message.text.replace('@', '')

    dialog_manager.dialog_data['chat_settings_username'] = chat_username
    await dialog_manager.switch_to(state=MainDialog.chat_info)


# Изменить интервал активности ботов в чате
async def interval_activity_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Получаем кол-во часов
    try:
        interval_activity_hours = int(message.text)
        if interval_activity_hours > 24 or interval_activity_hours < 1:
            await dialog_manager.event.answer('Введите число от 1 до 24')
            return
    except ValueError:
        await dialog_manager.event.answer('Введите число')
        return

    # Изменяем данные в БД
    username = dialog_manager.dialog_data.get('chat_settings_username')
    await db_change_chat(username, {'activity_interval_hours': interval_activity_hours})

    # Обновляем диалог
    await dialog_manager.switch_to(state=MainDialog.chat_info)


# Изменить вариативность в чате
async def work_mode_chance_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Получаем % диалога и вопроса
    try:
        # Разбиваем сообщение на части
        parts = message.text.strip().split()

        # Проверяем количество чисел
        if len(parts) != 2:
            await message.answer(
                "❌ Нужно отправить ровно два числа через пробел\n"
                "Пример: <code>60 40</code>"
            )
            return

        # Парсим числа
        dialog_chance = int(parts[0])
        question_chance = int(parts[1])

        # Проверяем валидность чисел
        if dialog_chance < 0 or question_chance < 0:
            await message.answer("❌ Проценты не могут быть отрицательными")
            return

        if (dialog_chance + question_chance) != 100:
            await message.answer(
                "❌ Сумма процентов должна быть равна 100%\n"
                f"У вас: {dialog_chance + question_chance}%"
            )
            return
    except ValueError:
        await message.answer(
            "❌ Нужно отправить целые числа\n"
            "Пример: <code>70 30</code>"
        )
        return

    # Изменяем данные в БД
    username = dialog_manager.dialog_data.get('chat_settings_username')
    await db_change_chat(username, {'question_chance': question_chance, 'dialog_chance': dialog_chance})

    # Обновляем диалог
    await dialog_manager.switch_to(state=MainDialog.chat_info)


# [Добавление бота] Получаем .session
async def get_session_input(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Константы путей
    TEMP_DIR = Path("bot/telethon/temp_files")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Проверка расширения
    if not message.document.file_name.lower().endswith('.session'):
        await message.answer("❌ Файл должен иметь расширение .session")
        return

    # Обработка файла
    session_path = TEMP_DIR / message.document.file_name
    try:
        # Скачивание файла
        await message.bot.download(
            message.document,
            destination=str(session_path)
        )

        # Сохранение пути
        dialog_manager.dialog_data["add_bot_session_path"] = str(session_path)
        await message.answer("Файл .session успешно получен")

        # Переход к следующему состоянию
        await dialog_manager.switch_to(AddUserbot.get_json)

    except Exception as e:
        await message.answer(f"Ошибка при обработке файла:\n{str(e)}")
        # Удаление файла в случае ошибки
        if session_path.exists():
            session_path.unlink()


# [Добавление бота] Получаем .json
async def get_json_input(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    # Константы путей
    TEMP_DIR = Path("bot/telethon/temp_files")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Проверка расширения
    if not message.document.file_name.lower().endswith('.json'):
        await message.answer("Файл должен иметь расширение .json")
        return

    # Обработка файла
    json_path = TEMP_DIR / message.document.file_name
    try:
        # Скачивание файла
        await message.bot.download(
            message.document,
            destination=str(json_path)
        )

        # Сохранение пути
        dialog_manager.dialog_data["add_bot_json_path"] = str(json_path)
        await message.answer("Файл .json успешно получен")

        # Переход к следующему состоянию
        await dialog_manager.switch_to(AddUserbot.get_proxy)

    except Exception as e:
        await message.answer(f"Ошибка при обработке файла:\n{str(e)}")
        # Удаление файла в случае ошибки
        if json_path.exists():
            json_path.unlink()


# [Добавление бота] Получаем proxy
async def get_proxy_input(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    proxy_data = message.text.strip()

    # Проверяем базовый формат (4 части через :)
    parts = proxy_data.split(':')
    if len(parts) != 4:
        await message.answer(
            "Неверный формат прокси. Должно быть: ip:port:login:pass\n"
            "Пример: 109.236.80.210:9999:rq7re0vcg1:QLdSi1IVMFupLYiv"
        )
        return

    ip, port, login, password = parts

    # Если все проверки пройдены - сохраняем
    dialog_manager.dialog_data["add_bot_proxy_dict"] = {
        "scheme": "http",
        "host": ip,
        "port": port,
        "login": login,
        "password": password,
        "full": proxy_data  # Сохраняем и оригинальную строку
    }

    await message.answer("Прокси успешно сохранен\n\n"
                         "<b>Начинаю конвертацию telethon сессии в pyrogram!\nЭто может занять до 1 минуты, ожидайте!</b>")
    await dialog_manager.switch_to(AddUserbot.result)