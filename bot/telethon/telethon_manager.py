import aiohttp
from urllib.parse import urlparse
from aiohttp_socks import ProxyConnector

from telethon import TelegramClient


# Проверяет валидность прокси через подключение к Telegram API
async def check_proxy_validity(proxy_dict: dict) -> dict:
    # Формируем URL прокси
    proxy_url = (
        f"{proxy_dict['scheme']}://"
        f"{proxy_dict['login']}:{proxy_dict['password']}@"
        f"{proxy_dict['host']}:{proxy_dict['port']}"
    )

    # Пытаемся подключиться к Telegram API через прокси
    connector = ProxyConnector.from_url(proxy_url)
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            try:
                # Делаем тестовый запрос к Telegram API
                async with session.get("https://api.telegram.org:443") as response:
                    if response.status == 200:
                        return {"result": True}
                    else:
                        return {
                            "result": False,
                            "result_text": f"Прокси не отвечает (код {response.status})"
                        }
            except Exception as e:
                return {
                    "result": False,
                    "result_text": f"Ошибка подключения через прокси: {str(e)}"
                }
    except Exception as e:
        return {
            "result": False,
            "result_text": f"Ошибка инициализации прокси: {str(e)}"
        }
    finally:
        await connector.close()


# Проверяет валидность сессии через Telethon
async def check_telethon_session(session_path: str) -> tuple:
    client = None
    try:
        client = TelegramClient(
            session=session_path,
            api_id=2040,
            api_hash='b18441a1ff607e10a989891a5462e627'
        )

        await client.connect()
        if not await client.is_user_authorized():
            return False, "Аккаунт не существует или сессия невалидна"

        me = await client.get_me()
        return True, {
            "id": me.id,
            "first_name": me.first_name,
            "username": me.username
        }
    except Exception as e:
        error_msg = str(e).lower()
        if "disconnect" in error_msg or "cannot send requests" in error_msg:
            return False, "Ошибка соединения с сервером Telegram"
        elif any(word in error_msg for word in ['auth', 'authorization', 'session']):
            return False, "Аккаунт не существует или сессия невалидна"
        return False, f"Неизвестная ошибка: {str(e)}"
    finally:
        if client and client.is_connected():
            await client.disconnect()