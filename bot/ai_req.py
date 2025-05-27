import json
import requests
import random

async def generate_chat_text(telegram_chat_title: str, api_key: str, mode: str = "question") -> str:
    # Загрузка промптов из JSON
    try:
        with open("prompts.json", "r", encoding="utf-8") as file:
            prompts = json.load(file)
    except FileNotFoundError:
        return "Error: prompts.json not found"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in prompts.json"

    # Поиск нужного промпта по mode
    prompt_data = next((p for p in prompts if p["mode"] == mode), None)
    if not prompt_data:
        return f"Error: No prompt found for mode '{mode}'"

    # Формирование промпта
    try:
        if mode == "question":
            prompt = prompt_data["prompt"].format(telegram_chat_title=telegram_chat_title)
        elif mode == "dialog":
            messages_count = random.randint(2, 5)  # Случайное количество сообщений
            prompt = prompt_data["prompt"].format(
                telegram_chat_title=telegram_chat_title,
                messages_count=messages_count
            )
        else:
            return "Error: Invalid generation mode"
    except KeyError as e:
        return f"Error: Missing placeholder {str(e)} in prompt"

    # Запрос к API
    url = "https://ask.chadgpt.ru/api/public/gpt-4o-mini"
    try:
        response = requests.post(
            url,
            json={
                "message": prompt,
                "api_key": api_key
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get('is_success'):
            return data['response']
        return f"API Error: {data.get('error_message', 'Unknown error')}"
    except Exception as e:
        return f"Request failed: {str(e)}"