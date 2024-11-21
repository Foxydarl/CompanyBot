import requests
import json
from datetime import datetime
import os
from HelperDB import *


def request_mess(msg, prompt, dialog_history):
    url = "https://api.edenai.run/v2/text/chat"
    msg = msg.strip()
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"}

    payload = {
        "providers": "openai",
        "settings": { "openai": "gpt-4o" } ,
        "text": msg,
        "chatbot_global_action": prompt ,
        "previous_history": dialog_history,
        "temperature": 0.0,
        "max_tokens": 150,
        "fallback_providers": "openai"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    print("-" * 80)
    print(result)
    return (result['openai']['generated_text'])

def get_mess(msg, prompt, use_history, dialog_history):
    if use_history == False:
        dialog_history = []
        return request_mess(msg, prompt, dialog_history)
    elif use_history == True:
        return request_mess(msg, prompt, dialog_history)


def getDateAndTime(self):
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def get_presentations():
    folder_path = 'presentations'
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.pdf') or file.endswith('.pptx')]

def get_videos():
    folder_path = 'videos'
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.mp4', '.mov'))]

def read_file(name_file):
    myfile = open(f"{name_file}.txt", "r")
    return myfile.read()

def write_file(name_file, text):
    myfile = open(f"{name_file}.txt", "w")
    return myfile.write(text)
def get_images():
    image_folder = 'styles'
    return [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

def notify(message):
    user_id = message.chat.id
    dialog_history = get_dialog_from_db(user_id)
    change_waiting_flag_true(user_id)
    if dialog_history:
        last_10_messages = dialog_history[-10:]
        formatted_history = "\n".join(
            [f"{entry['role']}: {entry['message']}" for entry in last_10_messages]
        )
    else:
        formatted_history = "История сообщений отсутствует."

    notification_text = (
        f"Новый запрос от пользователя:\n"
        f"Chat ID: {user_id}\n"
        f"Сообщение: {message.text}\n\n"
        f"Последние 10 сообщений:\n{formatted_history}\n\n"
        f"Для ответа используйте формат:\n"
        f"<chat_id> Сообщение: <текст ответа>"
    )
    return notification_text