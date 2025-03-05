import os
from datetime import datetime
from HelperDB2 import *
from openai import OpenAI
import requests

API_KEY = "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"
client = OpenAI(api_key=API_KEY)

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
    print(company_text)
    print(company_info)
    print(question_text)
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

def get_folders(path):
    return [os.path.join(path, folder) for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]

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

def request_mess(message, prompt, history):
    if not message or not isinstance(message, str) or message.strip() == "":
        return "Ошибка: сообщение пустое."

    if not prompt or not isinstance(prompt, str) or prompt.strip() == "":
        return "Ошибка: системный промпт отсутствует."

    model = "gpt-4o-mini"
    messages = [{"role": "system", "content": prompt}]
    
    if history and isinstance(history, list):
        messages.extend(history)
    
    messages.append({"role": "user", "content": message})  # Гарантия, что message не пустой

    print(messages)

    # Отправляем запрос
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    # Новый API OpenAI: `message` — это объект
    return response.choices[0].message.content

def get_mess(msg, prompt, use_history, dialog_history=None):
    if not msg or not isinstance(msg, str):  
        return "Ошибка: сообщение отсутствует."

    if not prompt or not isinstance(prompt, str):  
        return "Ошибка: промпт отсутствует."

    dialog_history = dialog_history if use_history and isinstance(dialog_history, list) else []
    
    return request_mess(msg, prompt, dialog_history)


'''
user_message = "напиши простой код на питоне"
# Пример истории диалога: можно передать список предыдущих сообщений
conversation_history = [
    {"role": "assistant", "content": "Sure, here's one:"},
    {"role": "user", "content": "I need another one, please."}
]



reply = chat_with_ai(user_message, prompt="Ты помощник по кодингу", history=conversation_history)
print(80 * "?")
print(reply)
print(80 * "?")'''


def getDateAndTime():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
