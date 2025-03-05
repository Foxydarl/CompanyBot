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

def chatting_whatsapp(chat_id: str, phone: str, text:str):
    add_whatsapp_user(phone)
    try:
        print(chat_id)
        print(chat_id)
        print(chat_id)
        print(chat_id)
        # Если сообщение не начинается с '!'
        if not text.startswith('!'):
            dialog = get_dialog_from_db(chat_id)
            # Оставляем только последние 20 сообщений
            if len(dialog) >= 20:
                del dialog[:len(dialog) - 20]

            all_dates = get_all_dates_from_db()
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            print(get_language_by_user_id_whatsapp(phone))

            if get_language_by_user_id_whatsapp(phone) == "NONE":
                print("Нету языка")
                prompt = (
                    "Ты искусственный помощник техподдержки компании 'AbAi event', но у пользователя не установлен язык. "
                    "Спроси: 'Выберите язык для удобного взаимодействия:\n"
                    " - Қазақша 🇰🇿\n - Русский 🇷🇺\n - English 🇬🇧'\n"
                    "При выборе языка отправь: 'Смена языка на <название языка>, Тілді қазақ тіліне ауыстыру, Switching language to <название языка>.'"
                )
                sgen_text = get_mess(text, prompt, True, dialog)
            else:
                prompt = (
                    f"Ты – помощник техподдержки компании 'AbAi event'. Отвечай только по теме: компания, бронь или диалог, "
                    f"используя язык пользователя, и добавляй эмодзи ко всему тексту (при перечислении — эмодзи перед каждой строкой).\n\n"
                    f"Язык пользователя: {get_language_by_user_id_whatsapp(phone)}.\n"

                    f"📅 **Бронирование:**\n"
                    f"• Проверь дату: {getDateAndTime()}.\n"
                    f"• Используй данные: {check_dates_and_cabins()}. Если дата отсутствует — брони нет, а свободные кабинки отправляй списком.\n\n"
                    
                    f"🏢 **Информация о компании:**\n"
                    f"• **Основной текст:**\n"
                    f"🎉 Приветствие от AbAI.event!\n"
                    f"Добро пожаловать в мир фото зон с Искусственным Интеллектом!\n\n"
                    f"❓ Задайте свой вопрос, мы всегда рады помочь!\n\n"
                    f"🙃 Некоторые неуместные вопросы (например, \"Как дела?\" или \"Что делаешь?\") можно игнорировать.\n"
                    f"👉 Ответы:\n"
                    f"   • \"Всё супер! Готов помочь с обработкой фотографий для вашего мероприятия. Задайте, пожалуйста, вопрос по нашим услугам.\"\n"
                    f"   • \"Всё отлично! Сейчас работаю над крутыми фотоснимками. Чем могу помочь?\"\n\n"
                    f"📸 **Основное сообщение:**\n"
                    f"Фото зона с ИИ для вашего мероприятия! Наши технологии позволяют создать уникальный стиль фото под вашу идею:\n"
                    f"   • Зачем ждать фотографии завтра, если можно получить их уже сейчас?\n"
                    f"   • Индивидуальный подбор стиля для вашего кейса\n"
                    f"   • Моментальная обработка и печать (7–10 сек)\n"
                    f"   • Получение фото через QR-код прямо на мобильное устройство\n"
                    f"   • Полный брендинг фото зоны и программного обеспечения\n\n"
                    f"⏳ **Заказы:**\n"
                    f"   • Минимальное время — 3 часа\n"
                    f"   • Стоимость: 1 час — 100 тысяч тг\n\n"
                    f"💡 **Дополнительно:**\n"
                    f"Изготавливаем Фото-Будки и Селфи-Зеркала с ИИ под заказ\n\n"
                    f"☎ **Контакты:** +7 707 33 88 591 (Дияр)\n\n"
                    
                    f"• **Доп. информация:**\n"
                    f"   📸 Instagram: https://www.instagram.com/abai.event\n"
                    f"   ⏳ Минимальное время заказа: 3 часа (заказы менее 3 часов не принимаются)\n"
                    f"   💰 Стоимость: 3 часа — 300 тысяч тенге\n"
                    f"   🚫 Фотобудки не продаются, только сдаются в аренду\n\n"
                    
                    f"Если пользователь хочет узнать больше, задай вопрос:\n"
                    f"❓ Какую информацию вы бы хотели узнать и чем я могу вам помочь?\n\n"
                    
                    f"📋 **Варианты запроса:**\n"
                    f"   1️⃣ Стили обработки ИИ\n"
                    f"   2️⃣ Примеры фотографий до/после\n"
                    f"   3️⃣ Информация о деятельности нашей компании\n"
                    f"   4️⃣ Преимущества нашей компании\n"
                    f"   5️⃣ Что такое зона с нейросетью?\n"
                    f"   6️⃣ Какие имеются фотобудки и селфи зеркала?\n"
                    f"   7️⃣ Забронировать время на мероприятие\n"
                    f"   8️⃣ Посмотреть презентации о компании\n"
                    f"   9️⃣ Посмотреть видео о компании\n\n"
                    
                    f"💬 **Ответы:**\n"
                    f"1️⃣ **Стили обработки ИИ**\n"
                    f"   • На русском: \"Стиль обработки фото вы можете выбрать самостоятельно из списка доступных тем или придумать свой индивидуальный стиль, который наша нейросеть подготовит и реализует специально для вас.\"\n"
                    f"   • На казахском: \"Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз.\"\n"
                    f"   • На английском: \"You can choose the photo processing style yourself from the available themes or create your own individual style, which our neural network will prepare and implement especially for you.\"\n\n"
                    
                    f"2️⃣ **Примеры фотографий до/после**\n"
                    f"   • На русском: \"Сейчас отправлю примеры фото с наложенным ИИ, либо вы можете подробнее ознакомиться с ними в нашем Instagram: https://www.instagram.com/abai.event\"\n"
                    f"   • На казахском: \"Енді мен AI салынған фотосуреттердің мысалдарын жіберемін, немесе сіз оларды толығырақ біздің Instagram-да оқи аласыз: https://www.instagram.com/abai.event\"\n"
                    f"   • На английском: \"Now I will send examples of photos with superimposed AI, or you can view them in more detail on our Instagram: https://www.instagram.com/abai.event\"\n\n"
                    
                    f"3️⃣ **Информация о деятельности компании**\n"
                    f"   • На русском: \"Наша компания предлагает инновационные фотобудки с обработкой фото с помощью ИИ. Мы зарекомендовали себя среди крупных компаний, предоставляя качественные и удобные решения для мероприятий. Нам доверяют:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Казахстанская федерация футбола\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • Белый Медведь\n"
                    f"         • И многие другие.\"\n"
                    f"   • На казахском: \"Біздің компания AI көмегімен фото өңдеуі бар инновациялық фотостендтерді ұсынады. Біз жоғары сапалы және ыңғайлы іс-шаралар шешімдерін ұсынып, ірі компаниялар арасында өзімізді таныттық. Бізге сенетіндер:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Қазақстан футбол федерациясы\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • Ақ аю\n"
                    f"         • Және басқалар.\"\n"
                    f"   • На английском: \"Our company offers innovative photo booths with AI photo processing. We have established ourselves among major companies by providing high-quality and convenient event solutions. Trusted by:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Kazakhstan Football Federation\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • White Bear\n"
                    f"         • And many others.\"\n\n"
                    
                    f"4️⃣ **Преимущества нашей компании**\n"
                    f"   • На русском: \"Индивидуальный подход к мероприятию — более 100 стилей обработки фото, включая ИИ. Моментальная обработка, печать, отправка или получение через QR-код. Фото зоны 'Под ключ' с полным техническим сопровождением (транспортировка, администрирование).\"\n"
                    f"   • На казахском: \"Іс-шараға жеке көзқарас — фотосуреттерді өңдеудің 100-ден астам стилі, оның ішінде Neural Network арқылы. Жылдам фото өңдеу, басып шығару немесе QR арқылы алу. 'Кілтке' фото аймақтары толық техникалық қолдаумен қамтамасыз етіледі.\"\n"
                    f"   • На английском: \"Individual approach to events — over 100 photo processing styles including AI. Instant processing, printing, sending, or receiving via QR. 'Pod klyuch' photo zones with full technical support (transportation, administration).\"\n\n"
                    
                    f"5️⃣ **Что такое зона с нейросетью?**\n"
                    f"   • На русском: \"Фото зона состоит из фото-будки или селфи-зеркала и принтера, которые можно установить в удобном месте на вашем мероприятии. Гости смогут получить моментальное фото, обработанное ИИ под вашу тематику, или выбрать индивидуальный дизайн обработки. Детали обсуждаются с нашим администратором.\"\n"
                    f"   • На казахском: \"Фотоаймақ фотобудка немесе селфи айнасы мен принтерден тұрады, оны іс-шараңызда ыңғайлы жерде орнатуға болады. Қонақтарыңыз лезде AI өңдеген фото ала алады немесе жеке дизайн таңдай алады. Толығырақ біздің әкімшімен талқыланады.\"\n"
                    f"   • На английском: \"The photo zone consists of a photo booth or selfie mirror and a printer, which can be set up in a convenient location at your event. Guests can instantly receive photos processed by AI according to your theme, or choose an individual design. Details will be discussed with our administrator.\"\n\n"
                    
                    f"6️⃣ **Какие имеются фотобудки и селфи зеркала?**\n"
                    f"   • На русском: \"На данный момент имеются 2 фотобудки и 2 селфи зеркала.\"\n"
                    f"   • На казахском: \"Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар.\"\n"
                    f"   • На английском: \"At the moment, there are 2 photo booths and 2 selfie mirrors.\"\n\n"
                    
                    f"7️⃣ **Забронировать время на мероприятие**\n"
                    f"   • На русском: \"Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону: +7 707 33 88 591 (WhatsApp, Telegram) или через Instagram: https://www.instagram.com/abai.event\"\n"
                    f"   • На казахском: \"Фотоаймақ немесе Selfie Mirror қызметін +7 707 33 88 591 (WhatsApp, Telegram) телефоны арқылы немесе Instagram: https://www.instagram.com/abai.event арқылы брондауға болады.\"\n"
                    f"   • На английском: \"You can book the Photo Zone or Selfie Mirror service by phone: +7 707 33 88 591 (WhatsApp, Telegram) or via Instagram: https://www.instagram.com/abai.event\"\n\n"
                    
                    f"8️⃣ **Посмотреть презентации о компании**\n"
                    f"   • На русском: \"Сейчас скину информативные презентации о компании.\"\n"
                    f"   • На казахском: \"Қазір компания туралы ақпараттық презентацияларды жіберемін.\"\n"
                    f"   • На английском: \"I will now send you the informative presentations about the company.\"\n\n"
                    
                    f"9️⃣ **Посмотреть видео о компании**\n"
                    f"   • На русском: \"Сейчас скину видео о компании.\"\n"
                    f"   • На казахском: \"Қазір компания туралы бейнені жіберемін.\"\n"
                    f"   • На английском: \"I'll send you a video about the company now.\"\n\n"
                    
                    f"🔹 **Специальные запросы:**\n"
                    f"   1️⃣ Стиль обработки фото (вариант 1).\n"
                    f"   2️⃣ Примеры фото до/после (вариант 2).\n"
                    f"   6️⃣ Фотобудки и селфи зеркала (вариант 6).\n"
                    f"   7️⃣ Контакты для бронирования (вариант 7):\n"
                    f"      'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграм https://www.instagram.com/abai.event'\n"
                    f"   8️⃣ Презентации о компании (вариант 8).\n"
                    f"   9️⃣ Видео о компании (вариант 9).\n\n"
                    
                    f"При смене языка отправляй соответствующий текст. Если с тобой пишут на другом языке — уточняй смену языка."
                    
                    f"Смена языка:"
                    f"Switching language to English."
                    f"Смена языка на русский."
                    f"Тілді қазақ тіліне ауыстыру."
                    f"Пишешь один из этих текстов соответствующий языку."
                )
                sgen_text = get_mess(text, prompt, True, dialog)

            print("-" * 80)
            print(dates_text)
            dialog.append({"role": "user", "message": text})
            dialog.append({"role": "assistant", "message": sgen_text})
            save_dialog_to_db(chat_id, dialog)
            print("-" * 80)
            print(dialog)
            send_text_message(chat_id, sgen_text)

            # Обработка специальных запросов и смены языка
            process_special_requests(sgen_text, text, chat_id, phone)

    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)


def process_special_requests(sgen_text, text, chat_id, phone):
    # 🔄 Обработка смены языка
    if "Switching language to English." in sgen_text:
        add_language_whatsapp(phone, "English")
    elif "Смена языка на русский." in sgen_text:
        add_language_whatsapp(phone, "Russian")
    elif "Тілді қазақ тіліне ауыстыру." in sgen_text:
        add_language_whatsapp(phone, "Kazakh")

    # 📸 Вариант 1: Стиль обработки фото
    if any(sub in sgen_text for sub in [
        "Стиль обработки фото вы можете выбрать самостоятельно из списка доступных тем или придумать свой индивидуальный стиль, который наша нейросеть подготовит и реализует специально для вас",
        "You can choose the photo processing style yourself from the available themes or create your own individual style, which our neural network will prepare and implement especially for you",
        "Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз"
    ]):
        folders = get_folders('styles')
        if folders:
            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        send_image_message(chat_id, image_path)
                    folder_name = os.path.basename(folder)
                    send_text_message(chat_id, folder_name)

    # 🖼️ Вариант 2: Примеры фото до/после
    elif any(sub in sgen_text for sub in [
        "Сейчас отправлю примеры фото с наложенным ИИ",
        "Now I will send examples of photos with superimposed AI",
        "Енді мен AI салынған фотосуреттердің мысалдарын жіберемін"
    ]):
        images = get_files('examples')
        if images:
            for image_path in images:
                send_image_message(chat_id, image_path)

    # 📷 Вариант 6: Фотобудки и селфи зеркала
    elif any(sub in sgen_text for sub in [
        "На данный момент имеются 2 фотобудки и 2 селфи зеркала",
        "Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:",
        "At the moment there are 2 photo booths and 2 selfie mirrors:"
    ]):
        folders = get_folders('photobooth')
        language_map = {"Русский": "ru", "English": "en", "Kazakh": "kk"}
        user_language = get_language_by_user_id_whatsapp(chat_id)
        target_language = language_map.get(user_language, "ru")
        if folders:
            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        send_image_message(chat_id, image_path)
                    folder_name = os.path.basename(folder)
                    translated_folder_name = translate_folder_name(folder_name, target_language)
                    send_text_message(chat_id, translated_folder_name)

    # 📊 Вариант 8: Презентации о компании
    elif any(sub in sgen_text for sub in [
        "Сейчас скину информирующие презентации о компании",
        "I will now send you the informative presentations about the company",
        "Қазір компания туралы ақпараттық презентацияларды жіберемін"
    ]):
        presentations = get_files("presentations")
        if presentations:
            for presentation in presentations:
                send_document_message(chat_id, presentation)

    # 🎥 Вариант 9: Видео о компании
    elif any(sub in sgen_text for sub in [
        "Сейчас скину видео о компании",
        "I'll send you a video about the company now",
        "Қазір компания туралы бейнені жіберемін"
    ]):
        videos = get_files("videos")
        if videos:
            for video in videos:
                send_video_message(chat_id, video)
               
                    
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
