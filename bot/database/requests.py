from aiogram.types import ChatFullInfo
from sqlalchemy import select, func, update, delete, insert
from datetime import datetime, timedelta

from bot.database.run_db import async_session
from bot.database.models import *


# Запуск/остановка работы ботов во всех чатах
async def db_change_all_chats_status(new_status: bool) -> bool:
    async with async_session() as session:
        try:
            # Обновляем статус во всех записях таблицы chats
            stmt = update(Chat).values(status=new_status)
            await session.execute(stmt)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при обновлении статуса чатов: {e}")
            return False


# Вывод краткой актуальной информации о чатах из БД
async def get_formatted_chats_list() -> list:
    async with async_session() as session:
        result = await session.execute(select(Chat))

        chat_status_list = [
            f"{i}) {chat.format_info()}"
            for i, chat in enumerate(result.scalars(), 1)
        ]

        return chat_status_list


# Удалить чат по username
async def db_delete_chat(username: str) -> bool:
    async with async_session() as session:
        try:
            # Удаляем чат с указанным username
            stmt = delete(Chat).where(Chat.username == username)
            result = await session.execute(stmt)
            await session.commit()

            # Проверяем, был ли удален хотя бы один чат
            return True if result.rowcount > 0 else False

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении чата @{username}: {e}")
            return False


# Добавить чат
async def db_add_chat(chat_full_info: ChatFullInfo) -> bool:
    async with async_session() as session:
        try:
            # Создаем новую запись чата
            new_chat = {
                "id": chat_full_info.id,
                "title": chat_full_info.title,
                "username": chat_full_info.username,
                "status": False,  # Статус по умолчанию - выключен
                "work_mode": "Не выбран",  # Режим работы по умолчанию
                "activity_interval_minutes": 120  # Интервал по умолчанию (2 часа)
            }

            # Выполняем запрос на добавление
            stmt = insert(Chat).values(**new_chat)
            await session.execute(stmt)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при добавлении чата: {e}")
            return False