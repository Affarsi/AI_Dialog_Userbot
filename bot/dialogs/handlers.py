from aiogram.types import CallbackQuery, Message

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput

from bot.database.requests import db_change_all_chats_status, db_delete_chat
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