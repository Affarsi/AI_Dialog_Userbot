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

    userbots_main_window,
    change_userbot_window,
    userbot_info_window,
    change_fullname_window,
    change_photo_window,
    
    change_promt_window,
    new_promt_dialog_window,
    new_promt_question_window,
)

add_userbot_dialog = Dialog(
    get_session_window,
    get_json_window,
    get_proxy_window,
    result_window,
)