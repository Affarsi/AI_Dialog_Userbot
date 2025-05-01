from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Group, SwitchTo, Start
from aiogram_dialog.widgets.kbd.state import Update
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.getters import main_menu_getter
from bot.dialogs.handlers import change_all_chats_status, delete_chat, add_chat
from bot.dialogs.states_groups import MainDialog

main_window = Window(
    Format(
        '<b>Список всех чатов:</b>\n'
        '{chat_status_list}'
    ),

    Group(
        Row(
            SwitchTo(Const('➕ Добавить чат'), id='add_chat', state=MainDialog.add_chat),
            SwitchTo(Const('➖ Удалить чат'), id='dell_chat', state=MainDialog.delete_chat)
        ),
        Button(Const('Настройка чата'), id='test4'),
        Row(
            Button(Const('🚀 Запустить всё'), id='all_start', on_click=change_all_chats_status),
            Button(Const('🛑 Остановить всё'), id='all_stop', on_click=change_all_chats_status)
        ),
        Update(),
    ),

    getter=main_menu_getter,
    state=MainDialog.main_menu,
)

delete_chat_window = Window(
    Const('<b>Введите логин чата, который желаете удалить:</b>\n\nНапример: @username_chat'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(delete_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.delete_chat,
)

add_chat_window = Window(
    Const('<b>Введите логин чата, который желаете добавить:</b>\n\nНапример: @username_chat'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(add_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.add_chat,
)