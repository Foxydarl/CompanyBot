import json
import requests
from config import token
import telebot

bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def welcome(message):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"
    }

    url = "https://api.edenai.run/v2/text/question_answer"
    payload = {
        "providers": "openai",
        "settings": { "openai": "gpt-4o" } ,
        "texts": [
            "Название компании 'Пример компании', занятые даты брони: 2024-11-15, 2024-11-16, 2024-11-17, 2024-11-18, 2024-11-20"
        ],
        'question': message.text,
        "examples_context": "Название компании 'Пример компании', занятые даты брони указаны выше.",
        "examples": [
            ["Занято ли 20 ноября?", "Да, занято"],
            ["Занято ли 21 ноября?", "Нет, 21 ноября свободно"],

        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 1.0
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if 'openai' in result and 'answers' in result['openai']:
            # Прямой ответ без Q и A
            answer = result['openai']['answers'][0]
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, "Не удалось получить ответ.")
    else:
        bot.send_message(message.chat.id, f"Ошибка: {response.status_code}")


if __name__ == "__main__":
    bot.infinity_polling()