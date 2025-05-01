from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Group, SwitchTo, Start
from aiogram_dialog.widgets.kbd.state import Update
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.getters import main_menu_getter, chat_info_getter
from bot.dialogs.handlers import change_all_chats_status, delete_chat, add_chat, settings_chat, change_chat_status, \
    change_chat_mode
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
        SwitchTo(Const('Настройка чата'), id='settings_chat', state=MainDialog.settings_chat),
        Row(
            Button(Const('🚀 Запустить всё'), id='all_start', on_click=change_all_chats_status),
            Button(Const('🛑 Остановить всё'), id='all_stop', on_click=change_all_chats_status)
        ),
        Update(),
    ),

    getter=main_menu_getter,
    state=MainDialog.main_menu,
)

chat_indo_window = Window(
    Format(
        '<b>Настройка чата @{username}:</b>\n'
        '\n'
        '<b>Название чата:</b> {title}\n'
        '<b>Статус:</b> {status}\n'
        '<b>Режим:</b> {work_mode}\n'
        '<b>Интервал активности:</b> {activity_interval_hours} час.\n'
        '\n'
        '<b>Вариативность:</b>\n'
        'Диалог - {dialog_chance}%\n'
        'Вопрос - {question_chance}%'
    ),

    Group(
        Row(
            Button(Const('🚀 Запустить'), id='chat_start', on_click=change_chat_status),
            Button(Const('🛑 Остановить'), id='chat_stop', on_click=change_chat_status),
        ),
        Button(Const('Изменить интервал активности'), id='test2'),
        Row(
            Button(Const('💬 Режим: "Диалог"'), id='dialog_mode', on_click=change_chat_mode),
            Button(Const('❓ Режим: "Вопрос"'), id='question_mode', on_click=change_chat_mode),
        ),
        Button(Const('Изменить % вариативности'), id='test3'),
        SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    ),

    getter=chat_info_getter,
    state=MainDialog.chat_info
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

settings_chat_window = Window(
    Const('<b>Введите логин чата, настройки которого желаете изменить:</b>\n\nНапример: @username_chat'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(settings_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.settings_chat,
)