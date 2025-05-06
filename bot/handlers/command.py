from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.dialogs.states_groups import MainDialog
from bot import filters

command_router = Router()

@command_router.message(Command("start"), filters.IsAdminFilter())
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainDialog.main_menu, mode=StartMode.RESET_STACK)