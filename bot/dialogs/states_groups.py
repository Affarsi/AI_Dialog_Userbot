from aiogram.filters.state import State, StatesGroup

class MainDialog(StatesGroup):
    main_menu = State()
    chat_info = State()

    delete_chat = State()
    add_chat = State()
    settings_chat = State()
    interval_activity_chat = State()
    work_mode_chance = State()

    userbots_main = State()
    change_userbot = State()
    userbot_info = State()
    change_fullname = State()
    change_photo = State()
    
    change_promt = State()
    new_promt_dialog = State()
    new_promt_question = State()

class AddUserbot(StatesGroup):
    get_session = State()
    get_json = State()
    get_proxy = State()
    result = State()
