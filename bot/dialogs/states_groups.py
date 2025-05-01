from aiogram.filters.state import State, StatesGroup

class MainDialog(StatesGroup):
    main_menu = State()
    delete_chat = State()