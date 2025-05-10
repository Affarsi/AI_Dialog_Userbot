from aiogram_dialog import DialogManager

from bot.database.queries import get_formatted_chats_list, db_get_chat, db_change_chat
from bot.database.run_db import async_session
from bot.database.models import Chat
from sqlalchemy import select

from bot.dialogs.states_groups import MainDialog


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