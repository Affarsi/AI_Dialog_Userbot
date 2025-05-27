from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Row, Group, SwitchTo, Start, Cancel, Button
# from aiogram_dialog.widgets.kbd.state import Update
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.getters import *
from bot.dialogs.handlers import *
from bot.dialogs.states_groups import MainDialog, AddUserbot

main_window = Window(
    Format(
        '<b>Список всех чатов:</b>\n\n'
        '{chat_status_list}'
    ),

    Group(
        # Update(),
        Row(
            SwitchTo(Const('➕ Добавить чат'), id='add_chat', state=MainDialog.add_chat),
            SwitchTo(Const('➖ Удалить чат'), id='dell_chat', state=MainDialog.delete_chat)
        ),
        SwitchTo(Const('Настройка чата'), id='settings_chat', state=MainDialog.settings_chat),
        Row(
            Button(Const('🚀 Запустить всё'), id='all_start', on_click=change_all_chats_status),
            Button(Const('🛑 Остановить всё'), id='all_stop', on_click=change_all_chats_status)
        ),
        SwitchTo(Const('Настройка ботов'), id='bots_main', state=MainDialog.userbots_main),
    ),

    getter=main_menu_getter,
    state=MainDialog.main_menu,
)

userbots_main_window = Window(
    Format('Список ботов:\n{session_list}'),
    Group(
        Start(Const('Добавить бота'), id='add_bot', state=AddUserbot.get_session),
        # Row(
        #     Start(Const('Изменить ник'), id='change_fullname', state=AddUserbot.),
        #     Start(Const('Изменить аватарку'), id='change_photo_profile', state=AddUserbot.),
        # ),
        SwitchTo(Const('Изменить промты'), id='change_promt', state=MainDialog.change_promt),
        SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    ),
    getter=userbots_main_getter,
    state=MainDialog.userbots_main
)

change_promt_window = Window(
    Format(
        '<b>Актуальные промты:</b>\n\n'
        '[telegram_chat_title] - название телеграмм канала, с которого происходит запрос,\n'
        '[messages_count] - скрипт составляет случайный диалог из 2-5 сообщений\n\n'
        '<b>Промт для диалога:</b>\n'
        '<code>{dialog_promt}</code>\n\n'
        '<b>Промт для вопросов:</b>\n'
        '<code>{question_promt}</code>'
    ),
    SwitchTo(Const('Изменить диалог'), id='change_dialog_promt', state=MainDialog.new_promt_dialog),
    SwitchTo(Const('Изменить вопрос'), id='change_question_promt', state=MainDialog.new_promt_question),
    SwitchTo(Const('Назад'), id='to_main_userbots_main', state=MainDialog.userbots_main),
    getter=change_promt_getter,
    state=MainDialog.change_promt
)

new_promt_dialog_window = Window(
    Const('Отправьте новый промт!\n\nНе забудьте использовать [telegram_chat_title] и [messages_count]'),
    MessageInput(get_new_dialog_promt_input, content_types=[ContentType.TEXT]),
    SwitchTo(Const('Назад'), id='to_change_promt', state=MainDialog.change_promt),
    state=MainDialog.new_promt_dialog
)

new_promt_question_window = Window(
    Const('Отправьте новый промт!\n\nНе забудьте использовать [telegram_chat_title]'),
    MessageInput(get_new_question_promt_input, content_types=[ContentType.TEXT]),
    SwitchTo(Const('Назад'), id='to_change_promt', state=MainDialog.change_promt),
    state=MainDialog.new_promt_question
)

get_session_window = Window(
    Const('Отправьте файл формата .session'),
    MessageInput(get_session_input, content_types=[ContentType.DOCUMENT]),
    Cancel(Const('Вернуться к списку ботов')),
    state=AddUserbot.get_session
)

get_json_window = Window(
    Const('Отправьте файл формата .json'),
    MessageInput(get_json_input, content_types=[ContentType.DOCUMENT]),
    Back(Const('Назад к .session')),
    Cancel(Const('Вернуться к списку ботов')),
    state=AddUserbot.get_json
)

get_proxy_window = Window(
    Const('Отправьте прокси ответным сообщением\n\nФормат: ip:port:login:pass'),
    MessageInput(get_proxy_input, content_types=[ContentType.TEXT]),
    Back(Const('Назад к .json')),
    Cancel(Const('Вернуться к списку ботов')),
    state=AddUserbot.get_proxy
)

result_window = Window(
    Format('{result_text}'),
    Cancel(Const('Назад')),
    getter=add_bot_result_getter,
    state=AddUserbot.result
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
        SwitchTo(Const('Изменить интервал активности'), id='activity_interval', state=MainDialog.interval_activity_chat),
        Row(
            Button(Const('💬 Режим: "Диалог"'), id='dialog_mode', on_click=change_chat_mode),
            Button(Const('❓ Режим: "Вопрос"'), id='question_mode', on_click=change_chat_mode),
        ),
        SwitchTo(Const('Изменить % вариативности'), id='work_mode_chance', state=MainDialog.work_mode_chance),
        SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    ),

    getter=chat_info_getter,
    state=MainDialog.chat_info
)

delete_chat_window = Window(
    Const('<b>Введите логин чата, который желаете удалить:</b>\n\n'
          'Формат: @username_chat\n'
          'Или ссылка: https://t.me/loginchatusername'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(delete_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.delete_chat,
)

add_chat_window = Window(
    Const('<b>Введите логин чата, который желаете добавить:</b>\n\n'
          'Формат: @username_chat\n'
          'Или ссылка: https://t.me/loginchatusername'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(add_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.add_chat,
)

settings_chat_window = Window(
    Const('<b>Введите логин чата, настройки которого желаете изменить:</b>\n\n'
          'Формат: @username_chat\n'
          'Или ссылка: https://t.me/loginchatusername'),
    SwitchTo(Const('Назад'), id='to_main_menu', state=MainDialog.main_menu),
    MessageInput(settings_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.settings_chat,
)

interval_activity_chat_window = Window(
    Const('<b>Введите новый интервал активности ботов (в часах):</b>\n\nот 1 до 24 часов.\n'
          'Данная переменная говорит, что каждое Nое кол-во часов бот будет запускаться и заходить в чат'),
    SwitchTo(Const('Назад'), id='to_chat_info', state=MainDialog.chat_info),
    MessageInput(interval_activity_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.interval_activity_chat,
)

work_mode_chance_window = Window(
    Const(
        '📊 <b>Настройка частоты режимов:</b>\n\n'
        'Отправьте два числа (сумма=100%), например:\n'
        '<code>60 40</code>\n'
        'что будет означать - 60% диалогов, 40% вопросов'
    ),
    SwitchTo(Const('Назад'), id='to_chat_info', state=MainDialog.chat_info),
    MessageInput(work_mode_chance_chat, content_types=[ContentType.TEXT]),
    state=MainDialog.work_mode_chance,
)