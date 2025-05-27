import pytz
import random
import asyncio
from config import Config
from aiogram_dialog import setup_dialogs

from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from bot.handlers.test import test_router
from bot.database.run_db import create_db   
from bot.handlers.command import command_router
from bot.dialogs.dialogs import main_dialog, add_userbot_dialog
from bot.apscheduler.scheduler import schedule_chat_activities

storage = MemoryStorage()
bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Инициализация планировщика


# Подключает все роутеры к диспетчеру.
def setup_routers(dp: Dispatcher) -> None:
    dp.include_routers(
        test_router,
        main_dialog,
        add_userbot_dialog,
        command_router,
    )


def get_random_interval():
    """Возвращает случайное количество секунд в диапазоне 45-85 минут"""
    return random.randint(45 * 60, 85 * 60)


async def schedule_random_job():
    """Запускает задачу и планирует следующее выполнение"""
    await schedule_chat_activities()
    # Планируем следующее выполнение
    scheduler.add_job(
        schedule_random_job,
        IntervalTrigger(seconds=get_random_interval()),
        id="main_job",
    )


# Действия при запуске планировщика
async def on_startup():
    # Запускаем первую задачу сразу или с небольшой задержкой
    scheduler.add_job(
        schedule_random_job,
        # Запускаем через 1 минуту после старта, чтобы бот успел инициализироваться
        IntervalTrigger(seconds=60),
        id="initial_job",
    )


async def main():
    # Установка таймзоны (лучше сделать в начале скрипта)
    pytz.timezone('Europe/Moscow')

    # Инициализация БД
    await create_db()

    # Настройка роутеров и диалогов
    setup_routers(dp)
    setup_dialogs(dp)

    # Запуск планировщика
    scheduler.start()
    await on_startup()

    # Запуск бота
    print('Бот запущен!')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())