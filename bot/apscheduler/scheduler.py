import asyncio
import random
from datetime import datetime

from bot.database.queries import db_get_chat, db_change_chat
from bot.pyrogram.userbot_manager import userbot_question, userbot_dialog


async def schedule_chat_activities():
    # Получаем все чаты
    chats_list = await db_get_chat()
    if not chats_list:
        return

    current_time = datetime.now()
    tasks = []

    for chat in chats_list:
        # Пропускаем неактивные чаты
        if not chat['status']:
            continue

        # Проверяем интервал активности
        time_diff = current_time - chat['last_activity']
        hours_diff = time_diff.total_seconds() / 3600

        # Находим чаты, в которых пора запустить активность
        if hours_diff >= chat['activity_interval_hours']:
            # Выбираем режим по вероятностям
            work_mode = random.choices(
                ['Вопрос', 'Диалог'],
                weights=[chat['question_chance'], chat['dialog_chance']],
                k=1
            )[0]

            print(f"💡 Выбран режим '{work_mode}' для чата {chat['username']} "
                  f"(Вопрос: {chat['question_chance']}%, Диалог: {chat['dialog_chance']}%)")

            if work_mode == 'Вопрос':
                task = asyncio.create_task(userbot_question(chat['username']))
            else:
                task = asyncio.create_task(userbot_dialog(chat['username']))

            tasks.append(task)

            # Обновляем дату последней активности чата
            await db_change_chat(chat['username'], {
                'last_activity': datetime.now(),
                'work_mode': work_mode  # Сохраняем выбранный режим
            })

    # Ждем завершения всех задач (опционально)
    if tasks:
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)