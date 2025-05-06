from aiogram.types import CallbackQuery, Message

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput

from bot.database.queries import db_change_all_chats_status, db_delete_chat, db_add_chat, db_change_chat
from bot.dialogs.states_groups import MainDialog


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
    telegram_chat = await dialog_manager.event.bot.get_chat(message.text)

    # Если чат не найден
    if not telegram_chat:
        await dialog_manager.event.answer(f"Чат @{message.text} не найден")
        await dialog_manager.switch_to(state=MainDialog.main_menu)
        return

    # Добавляем чат в БД
    result = await db_add_chat(telegram_chat)

    # Оповещаем пользователя и обновляем диалог
    await dialog_manager.event.answer(
        f"Чат @{message.text} успешно добавлен" if result else f"@{message.text} - ошибка базы данных"
    )
    await dialog_manager.switch_to(state=MainDialog.main_menu)


# Изменить настройки чата
async def settings_chat(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
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