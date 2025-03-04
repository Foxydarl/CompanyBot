import os
from datetime import datetime
from HelperDB2 import *

# Если используете Google Translate для translate_folder_name:
# from googletrans import Translator

def open_txt_files():
    """
    Вместо чтения из txt-файлов, забираем данные из таблицы info.
    Возвращаем кортеж (company_text, company_info, question_text).
    """
    company_text = get_info_by_key("company_text") or ""
    company_info = get_info_by_key("company_info") or ""
    question_text = get_info_by_key("question_text") or ""
    return company_text, company_info, question_text

def create_folders():
    """
    Создаёт нужные директории, если их нет.
    """
    for folder in ["presentations", "videos", "examples", "photobooth", "styles"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def translate_folder_name(folder_name, target_language):
    # Если нужно реально переводить названия папок, раскомментируйте googletrans
    # translator = Translator()
    # try:
    #     translation = translator.translate(folder_name, dest=target_language)
    #     return translation.text
    # except Exception as e:
    #     print(f"Ошибка перевода: {e}")
    #     return folder_name

    # Пока сделаем просто возврат того же названия
    return folder_name

def get_files(folder_path):
    """
    Возвращает список путей к файлам, у которых расширение .png, .jpg, .jpeg, .mp4, .mov, .pptx, .pdf
    """
    ends = ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.pptx', '.pdf')
    if not os.path.exists(folder_path):
        return []
    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(ends)
    ]

def display_files():
    """
    Показывает список папок (в текущей рабочей директории) для навигации при добавлении/удалении файлов.
    """
    current_directory = os.getcwd()
    folders = [f for f in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, f))]
    # В первых 3 могут быть системные каталоги (.git, venv и т.п.) – если хотите, пропустите их:
    sort_folders = "\n".join(sorted(folders)[3:])
    return f"Список папок:\n{sort_folders}"

def check_folder_contents(folder_path):
    """
    Возвращает список (строка для вывода, True/False есть ли подпапки, True/False есть ли файлы).
    """
    try:
        contents = os.listdir(folder_path)
        directories = [item for item in contents if os.path.isdir(os.path.join(folder_path, item))]
        files = [item for item in contents if os.path.isfile(os.path.join(folder_path, item))]

        if directories:
            text_dirs = "В данной папке есть подпапки. Укажите, в какую вы хотите перейти:\n"
            text_dirs += "\n".join(directories)
            return [text_dirs, True, None]
        elif not files and not directories:
            return ["Данная папка пуста. Отправьте файл, и я его добавлю.", False, False]
        else:
            file_list = "Вот файлы, находящиеся в данной папке:\n"
            file_list += "\n".join(files)
            return [file_list, False, True]
    except Exception as e:
        print(f"Ошибка при проверке содержимого папки: {e}")
        return ["Произошла ошибка при проверке содержимого папки.", False, False]

# Если вам нужен функционал запроса к внешнему API (OpenAI/ChatGPT), то здесь вы можете описать request_mess/get_mess.
# Я оставляю заглушку, так как в вашем коде это зависит от конкретных токенов/сервисов.
import requests
import json

def request_mess(msg, prompt, dialog_history):
    url = "https://api.edenai.run/v2/text/chat"
    msg = msg.strip()
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTkxNThjMzUtOTkyMi00NGU3LThmMmMtNDNlMDQwOGE5NmViIiwidHlwZSI6ImFwaV90b2tlbiJ9.E583qyGondeavZIvpXKVMJhxXYlSsOoHwSS4bIIkG0g"}

    payload = {
        "providers": "openai",
        "settings": { "openai": "gpt-4" } ,
        "text": msg,
        "chatbot_global_action": prompt ,
        "previous_history": dialog_history,
        "temperature": 0.0,
        "max_tokens": 300,
        "fallback_providers": "openai"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    print("-" * 80)
    print(result)
    return result['openai']['generated_text']
def get_mess(msg, prompt, use_history, dialog_history):
    if use_history == False:
        dialog_history = []
        return request_mess(msg, prompt, dialog_history)
    elif use_history == True:
        return request_mess(msg, prompt, dialog_history)


def getDateAndTime(self):
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")