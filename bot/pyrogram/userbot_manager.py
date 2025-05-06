import os
import asyncio
from typing import Union, List
from sqlite3 import OperationalError as SqliteOperationalError
from pyrogram import Client, enums
from sqlalchemy.exc import OperationalError as SqlAlchemyOperationalError

from config import Config


# Запускает указанное количество юзерботов
async def start_userbot_question(count: int = 1) -> Union[Client, List[Client], bool]:
    session_files = [f for f in os.listdir('bot/pyrogram/sessions')
                     if f.endswith('.session')]

    if not session_files:
        print("⚠️ Нет доступных сессий юзерботов в папке sessions/")
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
                    workdir="bot/pyrogram/sessions",
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
    client = await start_userbot_question(count=1)

    await client.join_chat(chat_username)
    print('Userbot вступил в чат')
    await client.send_message(chat_username, 'Hello World!')
    print('Userbot отправил сообщение')

    await client.stop()


# Работа юзерботов в режиме Диалог
async def userbot_dialog(chat_username: str):
    # Получаем двух юзерботов
    clients = await start_userbot_question(count=2)
    first_client, second_client = clients[0], clients[1]

    # dialog_text = await generate_dialog_text()  # Получаем текст диалога
    dialog_text = 'Фраза первого клиента!;Фраза Второго клиента; Фраза первого клиента; Фраза второго клиента!'

    # Разделяем фразы по точкам с запятой
    phrases = [phrase.strip() for phrase in dialog_text.split(';') if phrase.strip()]

    try:
        # Входим в чат (если еще не в нем)
        for client in clients:
            await client.join_chat(chat_username)

        # Поочередно отправляем фразы
        for i, phrase in enumerate(phrases):
            # Определяем текущего "говорящего"
            current_client = first_client if i % 2 == 0 else second_client

            print(f"💬 Юзербот {current_client.name} готовится отправить: {phrase}")

            # Имитируем печатание (корректная версия)
            typing_time = min(max(len(phrase) / 10, 8), 18)
            await current_client.send_chat_action(chat_username, enums.ChatAction.TYPING)

            # Создаем таск для отправки действия печатания
            chat_action_task = asyncio.create_task(
                send_continuous_chat_action(current_client, chat_username, typing_time)
            )

            # Ждем вычисленное время
            await asyncio.sleep(typing_time)

            # Отправляем сообщение и останавливаем действие печатания
            chat_action_task.cancel()
            await current_client.send_message(chat_username, phrase)
            print(f"✅ Сообщение отправлено: {phrase[:20]}...")

            # Пауза между репликами (2-4 секунды)
            await asyncio.sleep(2 + i % 3)  # Добавляем небольшую вариативность

    except Exception as e:
        print(f"❌ Ошибка в диалоге: {str(e)}")
    finally:
        # Останавливаем юзерботов
        for client in clients:
            await client.stop()


async def send_continuous_chat_action(client, chat_id, duration):
    """Отправляет действие печатания в течение указанного времени"""
    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            await asyncio.sleep(2.5)  # Chat action обновляется каждые 5 секунд
        except asyncio.CancelledError:
            break
        except Exception:
            break