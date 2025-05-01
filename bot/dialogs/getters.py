from aiogram_dialog import DialogManager

from bot.database.requests import get_formatted_chats_list, db_get_chat
from bot.database.run_db import async_session
from bot.database.models import Chat
from sqlalchemy import select

from bot.dialogs.states_groups import MainDialog


# Вывод краткой актуальной информации о чатах из БД
async def main_menu_getter(**kwargs):
    chat_status_list = await get_formatted_chats_list()
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