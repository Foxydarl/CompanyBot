import requests
import json
from datetime import datetime
import os
from HelperDB import *
from googletrans import Translator



def open_txt_files():
    with open("text.txt", "r", encoding="utf-8") as file:
        company_text = file.read().strip()
    with open("company_info.txt", "r", encoding="utf-8") as file:
        company_info = file.read().strip()
    with open("question.txt", "r", encoding="utf-8") as file1:
        question_text = file1.read().strip()
    return company_text, company_info, question_text

def create_folders():
    if not os.path.exists('presentations'):
        os.makedirs('presentations')
    if not os.path.exists('videos'):
        os.makedirs('videos')
    if not os.path.exists('examples'):
        os.makedirs('examples')
    if not os.path.exists('photobooth'):
        os.makedirs('photobooth')
    if not os.path.exists('styles'):
        os.makedirs('styles')

def translate_folder_name(folder_name, target_language):
    translator = Translator()
    try:
        translation = translator.translate(folder_name, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return folder_name  # В случае ошибки возвращаем оригинальное название

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

def read_file(name_file):
    myfile = open(f"{name_file}.txt", "r")
    return myfile.read()

def write_file(name_file, text):
    myfile = open(f"{name_file}.txt", "w")
    return myfile.write(text)

def get_files(file):
    file_folder = file
    ends = ('.png', '.jpg', '.jpeg', '.mp4', '.mov' '.pptx', '.pdf')
    return [os.path.join(file_folder, f) for f in os.listdir(file_folder) if f.lower().endswith(ends)]


#presentations\test8.mp4
#'file_id': 'CgACAgIAAxkBAAIaDWdHT3g1tLZebiRM4T4DPjFpZVrCAAKFZgACmhY5SnKCMqoXnGIONgQ', 'file_unique_id': 'AgADhWYAApoWOUo', 'file_size': 3764080, 'file_path': 'animations/file_83.mp4'}

def save_file(file, file_info):
    print()

def get_folders(path):
    return [os.path.join(path, folder) for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]

def display_files():
    current_directory = os.getcwd()  # Используем текущую рабочую директорию
    folders = [f for f in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, f))]
    sort_folders = "\n".join(sorted(folders)[3:])
    return f"Список папок:\n{sort_folders}"


def check_folder_contents(folder_path):
    try:
        contents = os.listdir(folder_path)
        directories = [item for item in contents if os.path.isdir(os.path.join(folder_path, item))]
        files = [item for item in contents if os.path.isfile(os.path.join(folder_path, item))]

        if directories:
            folders = "В данной папке есть подпапки. Укажите, в какую вы хотите перейти:\n"
            folders += "\n".join(directories)
            return [folders, True, None]
        elif not files and not directories:
            return ["Данная папка пуста. Отправьте файл, и я его добавлю.", False, False]
        else:
            file_list = "Вот файлы, находящиеся в данной папке:\n"
            file_list += "\n".join(files)
            return [file_list, False, True]
    except Exception as e:
        print(f"Ошибка при проверке содержимого папки: {e}")
        return ["Произошла ошибка при проверке содержимого папки.", False, False]