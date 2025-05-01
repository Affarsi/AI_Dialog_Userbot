from bot.database.requests import get_formatted_chats_list
from bot.database.run_db import async_session
from bot.database.models import Chat
from sqlalchemy import select

# Вывод краткой актуальной информации о чатах из БД
async def main_menu_getter(**kwargs):
    chat_status_list = await get_formatted_chats_list()
    chat_status_list = '\n\n'.join(chat_status_list)
    return {"chat_status_list": chat_status_list}