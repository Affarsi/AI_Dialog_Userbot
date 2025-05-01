from aiogram_dialog import Dialog

from bot.dialogs.windows import main_window, delete_chat_window, add_chat_window

main_dialog = Dialog(
    main_window,
    delete_chat_window,
    add_chat_window,
)