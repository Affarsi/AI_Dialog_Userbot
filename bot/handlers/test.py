from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.apscheduler.scheduler import schedule_chat_activities
from bot.dialogs.states_groups import MainDialog
from bot import filters

test_router = Router()

@test_router.message(Command("test"), filters.IsAdminFilter())
async def test_handler(message: Message, dialog_manager: DialogManager):
    await message.answer('Работа userbot`ов активирована')
    await schedule_chat_activities()