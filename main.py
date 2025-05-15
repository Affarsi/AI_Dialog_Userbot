import asyncio
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from bot.apscheduler.scheduler import schedule_chat_activities
from bot.database.run_db import create_db
from bot.handlers.command import command_router
from bot.dialogs.dialogs import main_dialog, add_userbot_dialog
from bot.handlers.test import test_router
from config import Config

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


# Действия при запуске планировщика
async def on_startup():
    # await schedule_chat_activities()
    scheduler.add_job(
        schedule_chat_activities,
        CronTrigger(hour="*/1"),
        id="main_job",
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