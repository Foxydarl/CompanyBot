import requests
import json
from datetime import datetime
import os


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
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def get_presentations():
    folder_path = 'presentations'
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.pdf') or file.endswith('.pptx')]

def get_videos():
    folder_path = 'videos'
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.mp4', '.mov'))]