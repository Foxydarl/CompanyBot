#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Переделанный WhatsApp‑бот с использованием WHAPI и Flask.
Функционал и команды заимствованы из кода Telegram‑бота (methods2 и HelperDB2),
но теперь администрирование реализовано через таблицу whatsapp_admins и колонку whatsapp_phone_number.
"""

from flask import Flask, request, jsonify
import requests
import subprocess
import re
import threading
import time
import os
from datetime import datetime

# Импорт вспомогательных функций для работы с БД и логикой бота.
# Предполагается, что в HelperDB2.py реализованы функции:
# add_whatsapp_user(phone), add_whatsapp_admin(phone), delete_whatsapp_admin(phone),
# check_whatsapp_admins() и другие функции (create_folders, createDataBase, и т.д.)
from methods2 import *
from HelperDB2 import *

# Создаём папки, базу данных и (при необходимости) наполняем её
create_folders()
createDataBase()
# fill_info_table()   # <-- раскомментируйте при первом запуске
# fill_qa_table()     # <-- если нужно заполнить таблицу QA

info_about_commands = (
    "Информация о командах:\n"
    "!пользователи\n"
    "!команды\n"
    "!очистить-историю-диалога\n"
    "!вопросы-ответы\n"
    "!удалить-вопрос-ответ\n"
    "!добавить-вопрос-ответ\n"
    "!информация\n"
    "!удалить-информацию\n"
    "!добавить-информацию\n"
    "!добавить-данные-о-кабинках\n"
    "!админы\n"
    "!удалить-админа\n"
    "!добавить-админа\n"
    "!добавить-колонку\n"
    "!удалить-колонку\n"
    "!обновить-бронь-даты\n"
    "!показать-таблицу\n"
    "!забронировать\n"
    "!добавить-дату\n"
    "!удалить-дату\n"
    "!добавить-папку\n"
    "!удалить-папку\n"
    "!добавить-файл\n"
    "!удалить-файл"
)

# ================== НАСТРОЙКИ WHAPI =====================
API_KEY = "JeckyS6ptE9PA2ZPbq9dZD10zOMtsqOS"

WHAPI_TEXT_URL = "https://gate.whapi.cloud/messages/text"
WHAPI_IMAGE_URL = "https://gate.whapi.cloud/messages/image"
WHAPI_DOCUMENT_URL = "https://gate.whapi.cloud/messages/document"
WHAPI_VIDEO_URL = "https://gate.whapi.cloud/messages/video"
PATCH_SETTINGS_ENDPOINT = "https://gate.whapi.cloud/settings"
LOCAL_TUNNEL_PORT = 5000

# ================= Функции отправки сообщений ================
def send_text_message(chat_id: str, text: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"to": chat_id, "body": text}
    try:
        response = requests.post(WHAPI_TEXT_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке текстового сообщения: {e}")
        return None

def send_image_message(chat_id: str, image_path: str, caption: str = ""):
    import base64
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    filename = os.path.basename(image_path)
    data = {
        "to": chat_id,
        "image": {"filename": filename, "data": encoded},
        "body": caption
    }
    try:
        response = requests.post(WHAPI_IMAGE_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке изображения: {e}")
        return None

def send_document_message(chat_id: str, doc_path: str, caption: str = ""):
    import base64
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    with open(doc_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    filename = os.path.basename(doc_path)
    data = {
        "to": chat_id,
        "document": {"filename": filename, "data": encoded},
        "body": caption
    }
    try:
        response = requests.post(WHAPI_DOCUMENT_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке документа: {e}")
        return None

def send_video_message(chat_id: str, video_path: str, caption: str = ""):
    import base64
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    with open(video_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    filename = os.path.basename(video_path)
    data = {
        "to": chat_id,
        "video": {"filename": filename, "data": encoded},
        "body": caption
    }
    try:
        response = requests.post(WHAPI_VIDEO_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        return None

# ================== Управление состоянием (для многошаговых команд) ==================
user_state = {}  # { chat_id: { "command": str, "temp_data": dict } }

def set_user_state(chat_id: str, command: str, temp_data=None):
    user_state[chat_id] = {"command": command, "temp_data": temp_data or {}}

def reset_user_state(chat_id: str):
    if chat_id in user_state:
        del user_state[chat_id]

def get_user_state(chat_id: str):
    return user_state.get(chat_id, None)

# ================== Обработка команд ==================
def handle_whatsapp_command(chat_id: str, phone: str, text: str) -> str:
    # Вместо проверки по chat_id, для WhatsApp проверяем, находится ли номер (phone) в таблице админов.
    whatsapp_admins = check_whatsapp_admins()  # функция возвращает список номеров админов
    is_admin = (phone in whatsapp_admins)
    if not is_admin:
        return "Вы не админ!"
    
    if text.startswith('!пользователи'):
        return format_users_table()
    
    elif text.startswith('!команды'):
        return info_about_commands

    elif text.startswith('!очистить-историю-диалога'):
        try:
            parts = text.split(" ", 1)
            if len(parts) > 1:
                param = parts[1].strip()
                if param == "мою":
                    result = clear_dialog(chat_id)
                else:
                    result = clear_dialog(int(param))
            else:
                result = clear_dialog(chat_id)
        except Exception:
            result = "⚠️ Введите существующий chat ID"
        return result

    elif text.startswith('!вопросы-ответы'):
        return format_QA_table()

    elif text.startswith('!удалить-вопрос-ответ'):
        try:
            qa = text.split(" ", 1)[1]
            result = delete_QA(qa)
        except Exception:
            result = "⚠️ Не получилось удалить вопрос-ответ."
        return result

    elif text.startswith('!добавить-вопрос-ответ'):
        try:
            text_after_command = text[len('!добавить-вопрос-ответ'):].strip()
            splitted = text_after_command.split('!', 1)
            if len(splitted) < 2:
                return "⚠️ Неверный формат. Пример: !добавить-вопрос-ответ ?Как дела? !Всё супер!"
            question_part = splitted[0].strip()
            answer_part = splitted[1].strip()
            if question_part.startswith('?'):
                question_part = question_part[1:].strip()
            result = add_QA(question_part, answer_part)
        except Exception as e:
            result = f"Ошибка при добавлении вопроса-ответа: {e}"
        return result

    elif text.startswith('!информация'):
        return format_info_table()

    elif text.startswith('!удалить-информацию'):
        try:
            info_key = text.split(" ", 1)[1]
            result = delete_info(info_key)
        except Exception:
            result = "⚠️ Не получилось удалить информацию."
        return result

    elif text.startswith('!добавить-информацию'):
        try:
            text_after_command = text[len('!добавить-информацию'):].strip()
            splitted = text_after_command.split('!', 1)
            if len(splitted) < 2:
                return "⚠️ Неверный формат. Пример: !добавить-информация ?ключ !контент"
            info_key = splitted[0].strip()
            content = splitted[1].strip()
            result = add_QA(info_key, content)
        except Exception as e:
            result = f"Ошибка при добавлении информации: {e}"
        return result

    elif text.startswith('!добавить-данные-о-кабинках'):
        set_user_state(chat_id, "add_cabins")
        return "Введите информацию о кабинках."

    elif text.startswith('!админы'):
        return format_admins_table()

    elif text.startswith('!удалить-админа'):
        try:
            admin_phone = text.split(" ", 1)[1]
            result = delete_whatsapp_admin(admin_phone)
        except Exception:
            result = "⚠️ Не получилось удалить админа."
        return result

    elif text.startswith('!добавить-админа'):
        try:
            admin_phone = text.split(" ", 1)[1]
            result = add_whatsapp_admin(admin_phone)
        except Exception:
            result = "⚠️ Не получилось добавить админа."
        return result

    elif text.startswith('!добавить-колонку'):
        try:
            column_name = text.split(" ", 1)[1]
            result = add_column(column_name)
        except Exception:
            result = "⚠️ Используйте: !добавить-колонку <название_продолжение>"
        return result

    elif text.startswith('!удалить-колонку'):
        try:
            column_name = text.split(" ", 1)[1]
            result = remove_column(column_name)
        except Exception:
            result = "⚠️ Используйте: !удалить-колонку <название_продолжение>"
        return result

    elif text.startswith('!обновить-бронь-даты'):
        try:
            parts = text.split(" ", 3)
            if len(parts) < 4:
                return "⚠️ Используйте: !обновить-бронь-даты <дата> <колонка> <статус>"
            _, date_str, column_name, status = parts
            if status not in ["free", "booked"]:
                return "В качестве статуса используйте <free> или <booked>"
            result = update_slot(date_str, column_name, status)
        except Exception:
            result = "⚠️ Используйте: !обновить-бронь-даты <дата> <колонка> <статус>"
        return result

    elif text.startswith('!показать-таблицу'):
        return format_table()

    elif text.startswith('!забронировать'):
        try:
            parts = text.split(" ", 2)
            if len(parts) < 3:
                return "⚠️ Используйте: !забронировать <дата> <колонка>"
            _, date_str, column_name = parts
            result = book_slot(date_str, column_name)
        except Exception:
            result = "⚠️ Используйте: !забронировать <дата> <колонка>"
        return result

    elif text.startswith('!добавить-дату'):
        data_val = text[len('!добавить-дату '):].strip()
        if data_val:
            result = save_data_to_db(data_val)
        else:
            result = "Не была указана дата. Пожалуйста, введите её."
        return result

    elif text.startswith('!удалить-дату'):
        data_val = text[len('!удалить-дату '):].strip()
        if data_val:
            result = delete_date_from_db(data_val)
        else:
            result = "Не была указана дата для удаления. Пожалуйста, введите её."
        return result

    # Многошаговые команды для файлов и папок
    elif text.startswith('!добавить-папку'):
        set_user_state(chat_id, "add_folder", temp_data={"current_path": os.getcwd()})
        return f"Укажите папку, в которой вы хотите создать новую папку.\nДоступные: {display_files()}"
    
    elif text.startswith('!удалить-папку'):
        set_user_state(chat_id, "delete_folder", temp_data={"current_path": os.getcwd()})
        return f"Укажите папку, в которой вы хотите удалить папку.\nДоступные: {display_files()}"
    
    elif text.startswith('!добавить-файл'):
        set_user_state(chat_id, "add_file", temp_data={"current_path": os.getcwd()})
        return f"Укажите папку, в которую вы хотите добавить файл.\nДоступные: {display_files()}"
    
    elif text.startswith('!удалить-файл'):
        set_user_state(chat_id, "delete_file", temp_data={"current_path": os.getcwd()})
        return f"Укажите папку, в которой вы хотите удалить файл.\nДоступные: {display_files()}"
    
    else:
        return None

# ================== Обработка НЕ команд и многошаговых сценариев ==================
def handle_whatsapp_non_command(chat_id: str, phone: str, text: str):
    state = get_user_state(chat_id)
    if state:
        # Пример многошагового сценария для добавления данных о кабинках
        if state["command"] == "add_cabins":
            from HelperDB2 import cursor, conn
            cursor.execute('INSERT OR REPLACE INTO info (info_key, content) VALUES (?, ?)', ("cabins_info", text))
            conn.commit()
            reset_user_state(chat_id)
            send_text_message(chat_id, "Информация о кабинках сохранена в БД под ключом 'cabins_info'.")
            return
        # Многошаговый сценарий для добавления папки
        elif state["command"] == "add_folder":
            current_path = state["temp_data"].get("current_path", os.getcwd())
            target_path = os.path.join(current_path, text)
            if not os.path.exists(target_path) or not os.path.isdir(target_path):
                send_text_message(chat_id, "Введите корректное название папки или напишите 'выйти'.")
                return
            state["command"] = "create_folder"
            state["temp_data"]["target_path"] = target_path
            send_text_message(chat_id, "Введите название новой папки, которую хотите создать, или напишите 'выйти'.")
            return
        elif state["command"] == "create_folder":
            if text.lower() == "выйти":
                reset_user_state(chat_id)
                send_text_message(chat_id, "Выхожу из этой функции.")
                return
            target_path = state["temp_data"].get("target_path")
            new_folder_name = text.strip()
            new_folder_path = os.path.join(target_path, new_folder_name)
            if os.path.exists(new_folder_path):
                send_text_message(chat_id, "Папка с таким названием уже существует. Попробуйте снова или напишите 'выйти'.")
                return
            os.makedirs(new_folder_path)
            reset_user_state(chat_id)
            send_text_message(chat_id, f"Папка '{new_folder_name}' успешно создана в '{target_path}'.")
            return
        # Здесь можно добавить аналогичную логику для delete_folder, add_file, delete_file и т.д.
        else:
            reset_user_state(chat_id)
    else:
        chatting_whatsapp(chat_id, phone, text)

def chatting_whatsapp(chat_id: str, phone: str, text: str):
    # Сохраняем пользователя по номеру WhatsApp
    add_whatsapp_user(phone)  # Важно: внутри этой функции параметр передаётся как кортеж (phone,)
    # Получаем историю диалога для данного chat_id
    dialog1 = get_dialog_from_db(chat_id)
    if len(dialog1) >= 20:
        dialog1 = dialog1[-20:]
    # Получаем доступные даты и дополнительную информацию
    all_dates = get_all_dates_from_db()
    dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
    company_text, company_info, question_text = open_txt_files()
    # Определяем язык пользователя
    user_lang = get_language_by_user_id(chat_id)
    if user_lang == "NONE":
        prompt = ("Ты искуственный помощник ... \n"
                  "Спроси про язык, на котором удобно общаться.")
        sgen_text = get_mess(text, prompt, True, dialog1)
    else:
        prompt = (f"Ты искуственный помощник ...\n"
                  f"Информационный текст: {company_text}\n"
                  f"Различная информация: {company_info}\n"
                  f"Список вопросов: {question_text}\n"
                  f"Сегодняшняя дата и время: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
                  f"Свободные/занятые даты: {check_dates_and_cabins()}\n"
                  f"Язык пользователя: {user_lang}\n")
        sgen_text = get_mess(text, prompt, True, dialog1)
    
    # Обновляем историю диалога и сохраняем её
    dialog1.append({"role": "user", "message": text})
    dialog1.append({"role": "assistant", "message": sgen_text})
    save_dialog_to_db(chat_id, dialog1)
    
    # Отправляем ответ через WHAPI
    send_text_message(chat_id, sgen_text)
    
    # Если обнаружена смена языка, обновляем его в БД
    if "Switching language to English." in sgen_text:
        add_language(chat_id, "English")
    elif "Смена языка на русский." in sgen_text:
        add_language(chat_id, "Russian")
    elif "Тілді қазақ тіліне ауыстыру." in sgen_text:
        add_language(chat_id, "Kazakh")
# ================== Flask‑приложение и вебхук ==================
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Получен вебхук от WHAPI:", data)
    if not data or "messages" not in data:
        return jsonify({"status": "no_messages"}), 400
    for msg in data["messages"]:
        if not msg.get("from_me", True):
            chat_id = msg.get("chat_id", "")
            phone = msg.get("from", "")
            text_body = ""
            if msg.get("type") == "text" and "text" in msg:
                text_body = msg["text"].get("body", "")
            print(f"➡️ Сообщение от {phone} (chat_id: {chat_id}): {text_body}")
            # При получении сообщения сохраняем пользователя через номер WhatsApp
            # (функция add_whatsapp_user реализована в HelperDB2)
            add_whatsapp_user(phone)
            if text_body.startswith("!"):
                response_text = handle_whatsapp_command(chat_id, phone, text_body)
                if response_text:
                    send_text_message(chat_id, response_text)
                else:
                    send_text_message(chat_id, "Неизвестная команда или недостаточно прав.")
            else:
                handle_whatsapp_non_command(chat_id, phone, text_body)
    return jsonify({"status": "ok"})

def start_localtunnel(port):
    cmd = ["lt", "--port", str(port), "--print-requests"]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
    )
    tunnel_url = None
    for line in process.stdout:
        print(line, end="")
        match = re.search(r"^your url is: (https://[^\s]+)", line)
        if match:
            tunnel_url = match.group(1)
            print(f"LocalTunnel URL: {tunnel_url}")
            break
    return process, tunnel_url

if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=LOCAL_TUNNEL_PORT)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    lt_process, tunnel_url = start_localtunnel(LOCAL_TUNNEL_PORT)
    if tunnel_url:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "webhooks": [
                {
                    "url": f"{tunnel_url}/webhook",
                    "events": [
                        {"type": "messages", "method": "post"},
                        {"type": "statuses", "method": "post"}
                    ]
                }
            ]
        }
        r = requests.patch(PATCH_SETTINGS_ENDPOINT, headers=headers, json=data)
        print("PATCH /settings:", r.status_code, r.text)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping LocalTunnel...")
        lt_process.terminate()
        lt_process.wait()
