# chat/gpt_client.py
import os
from openai import OpenAI

# Читаем ключ из переменных окружения
api_key = os.getenv("OPENAI_API_KEY")

# Проверка наличия ключа для информирования (опционально)
if not api_key:
    raise ValueError("OPENAI_API_KEY не найден в переменных окружения!")

# Инициализируем клиент с ключом из .env
client = OpenAI(
    api_key=api_key,
    base_url="https://openai.api.proxyapi.ru/v1",
)

SYSTEM_PROMPT = """Ты — эмпатичный психолог.
Отвечай с пониманием, поддержкой и мягким тоном.
Задавай уточняющие вопросы, если нужно.
Не давай медицинских диагнозов."""

def get_gpt_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content
