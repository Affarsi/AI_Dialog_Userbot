import asyncio

import pytz

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import (
    setup_dialogs, )

from bot.database.run_db import create_db
from bot.handlers import start_router
from bot.dialogs.dialogs import main_dialog
from config import Config

storage = MemoryStorage()
bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)


async def main():
    # Запуск БД
    pytz.timezone('Europe/Moscow')
    await create_db()

    # Настройка диалогов и обработчиков тг бота
    dp.include_routers(
        main_dialog,

        start_router
    )
    setup_dialogs(dp)

    # Старт тг бота
    print('Started!')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())