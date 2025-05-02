from aiogram.filters.state import State, StatesGroup

class MainDialog(StatesGroup):
    main_menu = State()
    chat_info = State()
    delete_chat = State()
    add_chat = State()
    settings_chat = State()
    interval_activity_chat = State()
    work_mode_chance = State()