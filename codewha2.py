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
import base64
import mimetypes

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
    "!удалить-дату"
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

def send_image_message(phone: str, image_path: str): 
    file_name = os.path.basename(image_path)   
    encoded_image = f"data:image/jpeg;name={file_name};base64,"
    with open(image_path, "rb") as f:
        encoded_image += base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "to": f"{phone}",
        "media": f"{encoded_image}"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(WHAPI_IMAGE_URL, json=payload, headers=headers)
        print(response.text)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке изображения: {e}")
        return None

def send_document_message(phone: str, doc_path: str, caption: str = ""):
    file_name = os.path.basename(doc_path)
    encoded_doc = f"data:application/pdf;name={file_name};base64,"
    with open(doc_path, "rb") as f:
        encoded_doc += base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "to": f"{phone}",
        "media": f"{encoded_doc}"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(WHAPI_DOCUMENT_URL, json=payload, headers=headers)
        print(response.text)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        return None

def send_video_message(phone: str, video_path: str):
    file_name = os.path.basename(video_path)
    encoded_video = f"data:video/mp4;name={file_name};base64,"
    with open(video_path, "rb") as f:
        encoded_video += base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "to": f"{phone}",
        "media": f"{encoded_video}"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(WHAPI_VIDEO_URL, json=payload, headers=headers)
        print(response.text)
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
        return format_admins_table_whatsapp()

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

def chatting_whatsapp(chat_id, phone, text):
    add_whatsapp_user(phone)
    try:
        print(text)
        if not text or not isinstance(text, str):  # Проверка текста сообщения
            send_text_message(chat_id, "Ошибка: Пустое сообщение. Введите текст.")
            return
        if not text.startswith('!'):
            dialog1 = get_dialog_from_db(chat_id)
            if len(dialog1) >= 20:
                del dialog1[:len(dialog1) - 20]
            all_dates = get_all_dates_from_db()
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            print(get_language_by_user_id(phone))
            #encoded_query = urllib.parse.quote(text)
            company_text, company_info, question_text = open_txt_files()
            if get_language_by_user_id_whatsapp(phone) == "NONE":
                print("Нету языка")
                sgen_text = get_mess(text, f"""Ты искуственный помощник технической поддержки компании 'AbAi event', но у пользователя на данный момент не установлен язык, твоя цель сейчас спросить про язык, на котором пользователю будет удобно общаться, вот вопрос который ты должен задавать:
                                                          'Выберите язык для удобного взаимодействия \n -Қазақша 🇰🇿 \n -Русский 🇷🇺 \n -English 🇬🇧 \n'
                                                          Если пользователь ответил, что хочет сменить язык например на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Все запросы и команды ты обрабатываешь на языке пользователя. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь
                                                          От темы не уходи, на вопросы, помимо темы с языками, ты не отвечаешь, ты переспрашиваешь у пользователя на который язык он хочет установить, спрашиваешь ты это, сразу на трёх языках, предлагая доступные варианты, твоя цель установить на каком языке хочет общаться пользователь и в зависимости от этого сменить его язык фразой 'Смена языка на 'название языка''""", True, dialog1)
            else:
                sgen_text = get_mess(text, f"""Ты искусственный помощник технической поддержки компании 'AbAi event', отвечающий на языке, смотря на каком с тобой общаются, только на вопроса по поводу компании, брони либо связанные как то с компанией, так же ты добавляешь для дизайна эмодзи ко всему тексту, который отправляешь, если есть перечисление, то по теме перечисления на каждую строчку добавляешь эмодзи
                                                          ты отвечаешь на вопросы по поводу компании и по поводу брони, так же ты просто разговариваешь с пользователем если он ведёт с тобой диалог, если человек спрашивает про бронь, ты отвечаешь занят день или нет, если занят, то какими будками, список занятых дат,
                                                          а также колонок: {check_dates_and_cabins()}, если в списке нету даты, значит нету брони, а также пиши пользователю свободные кабинки в виде списка если дата свободна. Сегодняшние дата и время - {getDateAndTime()} 
                                                          Информационный текст в котором расписаны случаи, как на что отвечать и различная информация: {company_text}
                                                          Различная информация про компанию и не только, имея данную информацию, ты отвечаешь на вопросы, смотря на каком языке с тобой общается пользователь: {company_info}
                                                          Если пользователь хочет забронировать день (оно находится под цифрой 7, после уточняющего вопроса), то ты должен скинуть ему следующие контактные данные: 'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграмм https://www.instagram.com/abai.event'
                                                          Если пользователь хочет узнать информацию о компании, то ты ему рассказываешь про компанию, так же спрашиваешь хочет ли пользователь получить больше информации про компанию, если он скажет, что хочет, то ты должен будешь спросить у него на языке пользователя информацию из данного текста: '{question_text}'
                                                          Если пользователь говорит, что хочет узнать про стили обработки ИИ(оно находится под цифрой 1, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас.'
                                                          Если пользователь говорит, что хочет узнать про примеры фотографий до/после(оно находится под цифрой 2, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас отправлю примеры фото с наложенным ИИ, либо же вы можете более подробно ознакомиться с ними в нашем Инстаграме https://www.instagram.com/abai.event', ссылку отправляешь только один раз и без лишних спец знаков, просто ссылку
                                                          Если пользователь говорит, что хочет узнать про фотобудки и селфи зеркала(оно находится под цифрой 6, после уточняющего вопроса), либо если пользователь просит скинуть фотографии фотобудок, то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала:' если русский, 'Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:' если казахский, 'At the moment there are 2 photo booths and 2 selfie mirrors:' если английский
                                                          Если пользователь говорит, что хочет посмотреть презентации о компании(оно находится под цифрой 8, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас скину информирующие презентации о компании'
                                                          Если пользователь говорит, что хочет посмотреть видео о компании(оно находится под цифрой 9, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас скину видео о компании'
                                                          Если пользователь хочет сменить язык на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Язык пользователя: {get_language_by_user_id(phone)}. Все запросы и команды ты обрабатываешь на языке пользователя и даже ответы на условия, в которых мы говорили отправлять только определённый текст, ты его переводишь и отправляешь на том языке, на котором с тобой пользователь говорил. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь
                                                          Если с тобой начинают говорить на другом языке отличного от установленного, поинтересуйся о смене языка пользователя
                                                          Если пользователь просит тебя показать фотобудки и зеркала, либо спрашивает как они выглядят, то ты добавляешь этот текст на языке пользователя к предыдущему тексту, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала'
                                                          Также могут быть дополнительные вопросы: {format_QA_table}
                                                          И может быть допоолнительная информация: {format_info_table}
                                                          """
                                                          ,True, dialog1)
            print("-" * 80)
            print(dates_text)
            dialog1.append({"role": "user", "content": [{ "type": "text", "text": f"{text}" }]})
            dialog1.append({"role": "assistant", "content": [{ "type": "text", "text": f"{sgen_text}" }]})
            save_dialog_to_db(chat_id, dialog1)
            print("-" * 80)
            print(dialog1)
            send_text_message(chat_id, sgen_text)
            if "Switching language to English." in sgen_text:
                add_language_whatsapp(phone, "English")
            if "Смена языка на русский." in sgen_text:
                add_language_whatsapp(phone, "Russian")
            if "Тілді қазақ тіліне ауыстыру." in sgen_text:
                add_language_whatsapp(phone, "Kazakh")
            elif "Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас" in sgen_text or "You can choose the photo processing style yourself from the list of available themes, or come up with your own individual style, which our neural network will prepare and implement especially for you" in sgen_text or "Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз" in sgen_text:
                folders = get_folders('styles')
                if folders:
                    for folder in folders:
                        images = get_files(folder)
                        if images:
                            # Отправляем все изображения
                            for image_path in images:
                                send_image_message(phone, image_path)
                            # После отправки всех изображений отправляем название папки
                            folder_name = os.path.basename(folder)
                            send_text_message(chat_id, folder_name)
            elif "Сейчас отправлю примеры фото с наложенным ИИ" in sgen_text or "Now I will send examples of photos with superimposed AI" in sgen_text or "Енді мен AI салынған фотосуреттердің мысалдарын жіберемін" in sgen_text:
                images = get_files('examples')
                if images:
                    # Отправляем все изображения
                    for image_path in images:
                        send_image_message(phone, image_path)
            elif "На данный момент имеются 2 фотобудки и 2 селфи зеркала" in sgen_text or "Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:" in sgen_text or "At the moment there are 2 photo booths and 2 selfie mirrors:" in sgen_text:
                folders = get_folders('photobooth')
                language_map = {
                    "Русский": "ru",
                    "English": "en",
                    "Kazakh": "kk"
                }

                if folders:
                    user_language = get_language_by_user_id(phone)
                    target_language = language_map.get(user_language, "ru")
                    for folder in folders:
                        images = get_files(folder)
                        if images:
                            for image_path in images:
                                send_image_message(phone, image_path)
                            # После отправки всех изображений отправляем название папки
                            folder_name = os.path.basename(folder)
                            translated_folder_name = translate_folder_name(folder_name, target_language)
                            send_text_message(chat_id, translated_folder_name)
            elif "Сейчас скину информирующие презентации о компании" in sgen_text or "I will now send you the informative presentations about the company" in sgen_text or "Қазір компания туралы ақпараттық презентацияларды жіберемін" in sgen_text:
                presentations = get_files("presentations")
                if presentations:
                    for presentation in presentations:
                        send_document_message(phone, presentation)
            elif "Сейчас скину видео о компании" in sgen_text or "I'll send you a video about the company now" in sgen_text or "Қазір компания туралы бейнені жіберемін" in sgen_text:
                videos = get_files("videos")
                if videos:
                    for video in videos:
                        send_video_message(phone, video)
    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)
               
                    
# ================== Flask‑приложение и вебхук ==================
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
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
    print("starttttttt")
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
