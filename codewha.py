# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import requests
import subprocess
import re
import threading
import time
import os

from HelperDB import *
from methods import *

"""
  Пример whatsapp.py, аналогичный telegram.py, но для WHAPI (WhatsApp).
  Использует Flask + локальный вебсервер + localtunnel для проброса webhook.
  Проверяет, начинается ли сообщение с '!' - тогда обрабатываем как команду,
  иначе работаем как чат-бот (GPT-логика), как в telegram.py.
"""

# ======================== НАСТРОЙКИ =============================

# Токен и URL WHAPI
API_KEY = "JeckyS6ptE9PA2ZPbq9dZD10zOMtsqOS"

# Точка для отправки текстовых сообщений
WHAPI_TEXT_URL = "https://gate.whapi.cloud/messages/text"
# Аналогичные точки для других типов:
WHAPI_IMAGE_URL = "https://gate.whapi.cloud/messages/image"
WHAPI_DOCUMENT_URL = "https://gate.whapi.cloud/messages/document"
WHAPI_VIDEO_URL = "https://gate.whapi.cloud/messages/video"
# ... и т.д.

# Для настройки webhooks в WHAPI
PATCH_SETTINGS_ENDPOINT = "https://gate.whapi.cloud/settings"

# Пример команды localtunnel. При необходимости поменяйте порт ниже (5000).
LOCAL_TUNNEL_PORT = 5000


# ======================== ИНИЦИАЛИЗАЦИЯ БАЗЫ =====================
create_folders()
createDataBase()

# Дополнительная шпаргалка по доступным командам:
info_about_commands = (
    "Информация о командах:\n"
    "!пользователи\n"
    "!админы\n"
    "!удалить-админа\n"
    "!добавить-админа\n"
    "!добавить-колонку <название_продолжение>\n"
    "!удалить-колонку <название_продолжение>\n"
    "!обновить-слот <дата> <колонка> <статус>\n"
    "!показать-таблицу\n"
    "!забронировать <дата> <колонка>\n"
    "!добавить-данные-о-кабинках\n"
    "!ожидающие-ответа\n"
    "!добавить-дату\n"
    "!удалить-дату\n"
    "!добавить-файл\n"
    "!остановить-чат\n"
    "!очистить-историю-диалога"
)


# ======================== ФУНКЦИИ ДЛЯ ОТПРАВКИ СООБЩЕНИЙ ========

def send_text_message(chat_id: str, text: str):
    """
    Отправляет простое текстовое сообщение в WhatsApp через WHAPI
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "to": chat_id,
        "body": text
    }
    try:
        response = requests.post(WHAPI_TEXT_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке текстового сообщения: {e}")
        return None


def send_image_message(chat_id: str, image_path: str, caption: str = ""):
    """
    Пример отправки изображения. 
    Формат запроса может отличаться, уточните в документации WHAPI.
    Ниже показан вариант с upload в виде base64 или URL.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Для примера считаем файл в base64. Для больших файлов может быть не очень оптимально.
    import base64
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    filename = os.path.basename(image_path)
    data = {
        "to": chat_id,
        "image": {
            "filename": filename,
            # "url": "https://some.link",  # Альтернативный вариант
            "data": encoded  # base64
        },
        "body": caption
    }
    try:
        response = requests.post(WHAPI_IMAGE_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке изображения: {e}")
        return None


def send_document_message(chat_id: str, doc_path: str, caption: str = ""):
    """
    Пример отправки документа (PDF, PPTX, и т.п.)
    Аналогично image/video. 
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    import base64
    with open(doc_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    filename = os.path.basename(doc_path)
    data = {
        "to": chat_id,
        "document": {
            "filename": filename,
            "data": encoded
        },
        "body": caption
    }
    try:
        response = requests.post(WHAPI_DOCUMENT_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке документа: {e}")
        return None


def send_video_message(chat_id: str, video_path: str, caption: str = ""):
    """
    Пример отправки видео. Аналогично.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    import base64
    with open(video_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    filename = os.path.basename(video_path)
    data = {
        "to": chat_id,
        "video": {
            "filename": filename,
            "data": encoded
        },
        "body": caption
    }
    try:
        response = requests.post(WHAPI_VIDEO_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        return None


# ====================== ВСПОМОГАТЕЛЬНАЯ ЛОГИКА ДЛЯ СОСТОЯНИЯ =====

"""
Пример заготовки для пошаговых команд. 
В Telegram боты используют next_step_handler, тут можно хранить в user_state 
шаг текущей команды. Если шагов много – придётся делать сложную FSM-логику.
"""
user_state = {}  # { phoneNumber: {"command": "...", "step": 1, "temp_data": {...}} }

def set_user_state(phone: str, command: str, step: int = 1, temp_data=None):
    user_state[phone] = {
        "command": command,
        "step": step,
        "temp_data": temp_data or {}
    }

def reset_user_state(phone: str):
    if phone in user_state:
        del user_state[phone]

def get_user_state(phone: str):
    return user_state.get(phone, None)


# ====================== ОСНОВНАЯ ЛОГИКА КОМАНД ==================

def handle_whatsapp_command(chat_id: str, phone: str, text: str):
    admin_chat_ids, admin_usernames = check_admins()
    # Считаем пользователя админом, если chat_id из вебхука есть в списке chat_id из БД
    is_admin = (chat_id in admin_chat_ids)

    if not is_admin:
        return "Вы не админ!"

    # Теперь по цепочке проверим, начинается ли текст с определённой команды:
    if text.startswith('!команды') and is_admin:
        return info_about_commands

    elif text.startswith('!пользователи') and is_admin:
        return format_users_table()

    elif text.startswith('!админы') and is_admin:
        return format_admins_table()

    elif text.startswith('!добавить-админа') and is_admin:
        try:
            # !добавить-админа 77001112233
            parts = text.split(" ", 1)
            phone_to_add = parts[1].strip()
            result = add_admin(phone_to_add)  # В БД admin (chat_id, username) = (phone, phone)
            return result
        except:
            return "⚠️ Не получилось добавить админа. Укажите номер."

    elif text.startswith('!удалить-админа') and is_admin:
        try:
            parts = text.split(" ", 1)
            phone_to_delete = parts[1].strip()
            result = delete_admin(phone_to_delete)
            return result
        except:
            return "⚠️ Не получилось удалить админа. Укажите номер."

    elif text.startswith('!добавить-колонку') and is_admin:
        try:
            column_name = text.split(" ", 1)[1]
            result = add_column(column_name)
            return result
        except:
            return "⚠️ Используйте: !добавить-колонку <название_продолжение>"

    elif text.startswith('!удалить-колонку') and is_admin:
        try:
            column_name = text.split(" ", 1)[1]
            result = remove_column(column_name)
            return result
        except:
            return "⚠️ Используйте: !удалить-колонку <название_продолжение>"

    elif text.startswith('!обновить-слот') and is_admin:
        try:
            # !обновить-слот <дата> <колонка> <статус>
            _, date_str, column_name, status = text.split(" ", 3)
            if status not in ["free", "booked"]:
                return "В качестве статуса используйте <free> или <booked>"
            result = update_slot(date_str, column_name, status)
            return result
        except:
            return "⚠️ Используйте: !обновить-слот <дата> <колонка> <статус>"

    elif text.startswith('!показать-таблицу') and is_admin:
        return format_table()

    elif text.startswith('!забронировать') and is_admin:
        try:
            # !забронировать <дата> <колонка>
            _, date_str, column_name = text.split(" ", 2)
            result = book_slot(date_str, column_name)
            return result
        except:
            return "⚠️ Используйте: !забронировать <дата> <колонка>"

    elif text.startswith('!добавить-данные-о-кабинках') and is_admin:
        # Упрощённо: просто просим следующей фразой указать данные и сразу пишем в файл
        # Либо можно перевести в пошаговый режим
        return "Введите информацию о кабинках одной следующей сообщением (после этого используйте !завершить-кабинки)."

    elif text.startswith('!завершить-кабинки') and is_admin:
        # Допустим, пользователь отправил всё в диалоге отдельно, мы можем взять последние сообщения, 
        # но это требует сложной логики. Для простоты — допустим, всё уже записано.
        return "Информация о кабинках успешно добавлена (упрощённый пример)."

    elif text.startswith('!добавить-дату') and is_admin:
        try:
            # !добавить-дату 2025-03-10
            date_val = text.replace('!добавить-дату', '').strip()
            result = save_data_to_db(date_val)
            return result
        except:
            return "Не была указана дата или неверный формат."

    elif text.startswith('!удалить-дату') and is_admin:
        try:
            date_val = text.replace('!удалить-дату', '').strip()
            result = delete_date_from_db(date_val)
            return result
        except:
            return "Не была указана дата для удаления."

    elif text.startswith('!очистить-историю-диалога'):
        # !очистить-историю-диалога или !очистить-историю-диалога 123456
        try:
            parts = text.split(" ", 1)
            if len(parts) == 1:
                # без аргументов – чистим диалог для текущего chat_id
                result = clear_dialog(chat_id)
            else:
                # если указали другой chat_id
                target_id = parts[1].strip()
                result = clear_dialog(target_id)
            return result
        except:
            return "⚠️ Введите корректный chat ID"

    elif text.startswith('!команды') and not is_admin:
        return "Команда доступна только для админов."

    # Пример, когда команда не распознана
    return None


def handle_whatsapp_non_command(chat_id: str, phone: str, text: str):
    """
    Аналог GPT-логики, как в telegram.py, если сообщение не начинается с '!'
    """
    # Аналог add_user(message) – в telegram.py мы пишем:
    # add_user(message). Тут:
    try:
        # Пытаемся добавить пользователя в БД
        # В telegram.py: INSERT INTO users(telegramChatId, telegramUserId)
        # Здесь: INSERT INTO users(whatsappPhoneNumber) ...
        cursor.execute(
            "INSERT INTO users (whatsappPhoneNumber) VALUES (?)",
            (phone,)
        )
        conn.commit()
    except:
        pass

    # Забираем историю диалога
    dialog1 = get_dialog_from_db(chat_id)
    if len(dialog1) >= 20:
        dialog1 = dialog1[-20:]  # ограничиваем размер

    # Логика формирования промпта – те же тексты, что в telegram.py
    all_dates = get_all_dates_from_db()
    dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."

    company_text, company_info, question_text = open_txt_files()

    # Язык пользователя
    user_lang = get_language_by_user_id(chat_id)
    if not user_lang or user_lang == "NONE":
        # Аналог вашей логики:
        prompt = (
            "Ты искуственный помощник техподдержки 'AbAi event', но язык у пользователя не установлен. "
            "Спроси его на трёх языках (RU/KZ/EN) - на каком языке удобнее общаться. "
            "Пока не отвечай ни на что другое."
        )
        sgen_text = get_mess(
            text,
            prompt,
            True,  # use_history
            dialog1
        )
    else:
        # Основной промпт, аналогичный telegram.py
        prompt = (
            f"Ты искусственный помощник 'AbAi event', отвечающий на {user_lang}. "
            f"Список занятых дат и кабинок:\n{check_dates_and_cabins()} \n"
            f"Текущая дата/время: {getDateAndTime(None)} \n"
            f"Текст компании: {company_text}\n"
            f"Информация о компании: {company_info}\n"
            f"Если просят забронировать – дай контакты. Если хотят сменить язык – смени. И т.д."
        )
        sgen_text = get_mess(text, prompt, True, dialog1)

    # Добавляем в историю и сохраняем
    dialog1.append({"role": "user", "message": text})
    dialog1.append({"role": "assistant", "message": sgen_text})
    save_dialog_to_db(chat_id, dialog1)

    # Отправляем полученный ответ
    send_text_message(chat_id, sgen_text)

    # Проверка на смену языка
    if "Switching language to English." in sgen_text:
        add_language(chat_id, "English")
    elif "Смена языка на русский." in sgen_text:
        add_language(chat_id, "Russian")
    elif "Тілді қазақ тіліне ауыстыру." in sgen_text:
        add_language(chat_id, "Kazakh")

    # Аналоги проверок на фразы "Сейчас отправлю примеры", "На данный момент имеются 2 фотобудки" и т.д.
    # Если нужно – аналогично telegram.py рассылаем файлы:
    if ("Стиль обработки фото" in sgen_text) or ("choose the photo processing style" in sgen_text):
        # отправляем все папки из styles
        folders = get_folders('styles')
        if folders:
            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        send_image_message(chat_id, image_path)  # caption опционально
                    # отправляем название папки
                    folder_name = os.path.basename(folder)
                    send_text_message(chat_id, folder_name)

    if ("Сейчас отправлю примеры фото" in sgen_text):
        images = get_files('examples')
        if images:
            for img in images:
                send_image_message(chat_id, img)

    if ("На данный момент имеются 2 фотобудки и 2 селфи зеркала" in sgen_text) or \
       ("2 фотостенд және 2 селфи айнасы" in sgen_text) or \
       ("2 photo booths and 2 selfie mirrors" in sgen_text):
        folders = get_folders('photobooth')
        if folders:
            # Определим язык для перевода подпапок (пример)
            language_map = {
                "Russian": "ru",
                "English": "en",
                "Kazakh": "kk"
            }
            target_language = language_map.get(user_lang, "ru")

            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        send_image_message(chat_id, image_path)
                    folder_name = os.path.basename(folder)
                    translated_folder_name = translate_folder_name(folder_name, target_language)
                    send_text_message(chat_id, translated_folder_name)

    if ("Сейчас скину информирующие презентации о компании" in sgen_text):
        presentations = get_files("presentations")
        if presentations:
            for p in presentations:
                send_document_message(chat_id, p)

    if ("Сейчас скину видео о компании" in sgen_text):
        videos = get_files("videos")
        if videos:
            for v in videos:
                send_video_message(chat_id, v)


# ======================== Flask-приложение =======================

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Точка приёма сообщений от WHAPI. Аналог on_message у Telegram.
    """
    data = request.json
    print("📩 Получен вебхук от WHAPI:", data)
    print("-" * 80)

    # Проверяем, что тело запроса не пустое и содержит "messages"
    if not data or "messages" not in data:
        return jsonify({"status": "no_messages"}), 400

    # Перебираем все сообщения из списка
    for msg in data["messages"]:
        # Проверяем, что сообщение не от нашего бота (from_me == False)
        if not msg.get("from_me", True):
            # chat_id = "77012528428@s.whatsapp.net" и т.п.
            chat_id = msg.get("chat_id", "")

            # Номер отправителя (в вашем JSON лежит в msg["from"])
            phone_number = msg.get("from", "")

            # Если тип сообщения "text", то извлекаем тело в text_body
            # Иначе оставляем пустую строку (или добавьте свой обработчик)
            text_body = ""
            if msg.get("type") == "text" and "text" in msg:
                text_body = msg["text"].get("body", "")

            print(f"➡️ Получено сообщение: '{text_body}' от номера: {phone_number}")

            # Если текст сообщения начинается с '!', считаем это командой
            if text_body.startswith('!'):
                result = handle_whatsapp_command(chat_id, phone_number, text_body)
                if result:
                    send_text_message(chat_id, result)
                else:
                    send_text_message(chat_id, "Неизвестная команда или у вас нет прав.")
            else:
                # Иначе обрабатываем как GPT-диалог
                handle_whatsapp_non_command(chat_id, phone_number, text_body)

    return jsonify({"status": "ok"})


# Функции для старта localtunnel и запуска Flask:
def start_localtunnel(port):
    cmd = ["lt", "--port", str(port), "--print-requests"]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
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
        # Прописываем webhook в настройках WHAPI
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
