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


# Получить информацию о чате по username
async def db_get_chat(username: str) -> dict or None:
    async with async_session() as session:
        try:
            # Получаем чат из базы данных
            result = await session.execute(
                select(Chat).where(Chat.username == username)
            )
            chat = result.scalar_one_or_none()

            if chat:
            # Формируем словарь с данными чата
                return {
                    'id': chat.id,
                    'title': chat.title,
                    'username': chat.username,
                    'status': "🟢" if chat.status else "🔴",
                    'work_mode': chat.work_mode,
                    'activity_interval_hours': chat.activity_interval_hours,
                    'dialog_chance': chat.dialog_chance,
                    'question_chance': chat.question_chance
                }
            return None

        except Exception as e:
            print(f"Ошибка при получении чата @{username}: {e}")
            return


# Изменить информацию о чате по username
async def db_change_chat(username: str, new_chat_data: dict[str, any]) -> bool:
    async with async_session() as session:
        try:
            # Проверяем, что есть что обновлять
            if not new_chat_data:
                return False

            # Создаем запрос на обновление
            stmt = update(Chat) \
                .where(Chat.username == username) \
                .values(**new_chat_data)

            # Выполняем запрос
            result = await session.execute(stmt)
            await session.commit()

            # Проверяем, был ли обновлен хотя бы один чат
            return True if result.rowcount > 0 else False

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при обновлении чата @{username}: {e}")
            return False
