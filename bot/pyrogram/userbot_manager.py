import os
import asyncio
from typing import Union, List
from sqlite3 import OperationalError as SqliteOperationalError
from pyrogram import Client, enums
from sqlalchemy.exc import OperationalError as SqlAlchemyOperationalError

from bot.ai_req import generate_chat_text
from config import Config


# Запускает указанное количество юзерботов
async def start_userbot_question(count: int = 1) -> Union[Client, List[Client], bool]:
    session_files = [f for f in os.listdir('bot/pyrogram/temp_files')
                     if f.endswith('.temp_files')]

    if not session_files:
        print("⚠️ Нет доступных сессий юзерботов в папке temp_files/")
        return False

    clients = []
    attempts = 0
    max_attempts = 3  # Максимальное количество попыток для каждого юзербота

    while len(clients) < count and attempts < max_attempts:
        for session_file in session_files:
            if len(clients) >= count:
                break

            session_name = os.path.splitext(session_file)[0]

            try:
                print(f"🔄 Пытаюсь запустить юзербота: {session_name}")

                # Проверяем, не запущен ли уже этот юзербот
                if any(c.name == session_name for c in clients):
                    continue

                # Создаем клиент Pyrogram
                client = Client(
                    name=session_name,
                    workdir="bot/pyrogram/temp_files",
                    api_id=Config.api_id,
                    api_hash=Config.api_hash,
                )

                await client.start()
                print(f"✅ Успешно запущен юзербот: {session_name}")
                clients.append(client)

            except (ConnectionError, SqliteOperationalError, SqlAlchemyOperationalError) as e:
                if "database is locked" in str(e):
                    print(f"⏳ БД заблокирована у {session_name}, пробую следующего...")
                else:
                    print(f"⏳ Ошибка подключения у {session_name}, пробую следующего...")
                continue

            except Exception as e:
                print(f"❌ Критическая ошибка у {session_name}: {type(e).__name__} - {e}")
                continue

        if len(clients) < count:
            print(f"🕒 Не удалось запустить достаточно юзерботов. Осталось попыток: {max_attempts - attempts - 1}")
            attempts += 1
            await asyncio.sleep(60)

    if not clients:
        print("❌ Не удалось запустить ни одного юзербота")
        return False

    return clients[0] if count == 1 else clients


# Работа юзербота в режиме Вопрос
async def userbot_question(chat_username: str):
    try:
        client = await start_userbot_question(count=1)
        if not client:
            return False

        # Получаем информацию о чате для title
        chat = await client.get_chat(chat_username)

        # Генерируем вопрос
        question_text = await generate_chat_text(
            chat.title,
            Config.chad_gpt_token,
            mode="question"
        )

        if question_text.startswith(("API Error", "Request failed")):
            print(f"Ошибка ИИ при генерации вопроса: {question_text}")
            return False

        await client.join_chat(chat_username)
        await client.send_chat_action(chat_username, enums.ChatAction.TYPING)
        await asyncio.sleep(5)
        await client.send_message(chat_username, question_text)
        print(f'Бот отправил вопрос: {question_text}')
        return True

    except Exception as e:
        print(f"Error in userbot_question: {type(e).__name__} - {e}")
        return False
    finally:
        if 'client' in locals():
            await client.stop()


# Работа юзерботов в режиме Диалог
async def userbot_dialog(chat_username: str):
    try:
        clients = await start_userbot_question(count=2)
        if not clients or len(clients) < 2:
            return False

        first_client, second_client = clients[0], clients[1]

        # Получаем информацию о чате для title
        chat = await first_client.get_chat(chat_username)

        # Генерируем диалог
        dialog_text = await generate_chat_text(
            chat.title,
            Config.chad_gpt_token,
            mode="dialog"
        )
        print(dialog_text)
        if dialog_text.startswith(("API Error", "Request failed")):
            print(f"Ошибка ИИ при генерации диалога: {dialog_text}")
            return False

        # Разделяем фразы
        phrases = [phrase.strip() for phrase in dialog_text.split(';') if phrase.strip()]

        # Входим в чат
        for client in clients:
            await client.join_chat(chat_username)

        # Отправляем фразы поочередно
        for i, phrase in enumerate(phrases):
            current_client = first_client if i % 2 == 0 else second_client
            print(f"💬 Юзербот {current_client.name} готовится отправить: {phrase}")

            typing_time = min(max(len(phrase) / 10, 8), 18)
            await current_client.send_chat_action(chat_username, enums.ChatAction.TYPING)
            chat_action_task = asyncio.create_task(
                send_continuous_chat_action(current_client, chat_username, typing_time)
            )
            await asyncio.sleep(typing_time)
            chat_action_task.cancel()
            await current_client.send_message(chat_username, phrase)
            print(f"✅ Сообщение отправлено: {phrase[:20]}...")
            await asyncio.sleep(2 + i % 3)

        return True

    except Exception as e:
        print(f"❌ Ошибка в диалоге: {str(e)}")
        return False
    finally:
        for client in clients:
            await client.stop()


# Отправляет действие печатания в течение указанного времени
async def send_continuous_chat_action(client, chat_id, duration):
    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            await asyncio.sleep(2.5)  # Chat action обновляется каждые 5 секунд
        except asyncio.CancelledError:
            break
        except Exception:
            break