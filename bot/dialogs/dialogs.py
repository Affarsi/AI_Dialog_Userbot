from aiogram_dialog import Dialog

from bot.dialogs.windows import *

main_dialog = Dialog(
    main_window,
    chat_indo_window,
    delete_chat_window,
    add_chat_window,
    settings_chat_window,
    interval_activity_chat_window,
    work_mode_chance_window,
)