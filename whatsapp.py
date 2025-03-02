from flask import Flask, request, jsonify
import requests
from methods import *
import subprocess
import re
import threading
import time

# ДАННЫЕ ИЗ WHAPI
AUTH_TOKEN_NGROK = "2tfigBPDuyvTWHRJrtH0yEi3tVp_6WfQL6CmhtWiVw5weK38r"
API_KEY = "JeckyS6ptE9PA2ZPbq9dZD10zOMtsqOS"
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
PATCH_SETTINGS_ENDPOINT = f"https://gate.whapi.cloud/settings"
create_folders()
createDataBase()
# Инициализация Flask-приложения
app = Flask(__name__)

def start_localtunnel(port):
    # Запускаем LocalTunnel и ждём, пока он выведет публичный URL
    # Параметр --print-requests покажет детальные логи (можно убрать)
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
        print(line, end="")  # Можно логировать всё, что пишет lt
        match = re.search(r"^your url is: (https://[^\s]+)", line)
        if match:
            tunnel_url = match.group(1)
            print(f"LocalTunnel URL: {tunnel_url}")
            break
    
    # В этот момент LocalTunnel продолжает работать в фоне,
    # а мы уже знаем public URL. Возвращаем process + URL.
    return process, tunnel_url

# Функция для отправки сообщения
def send_message(chat_id, text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "to": chat_id,
        "body": text,
    }
    print("📤 Отправка сообщения в Whapi:", data)  # Логируем отправку
    response = requests.post(WHAPI_URL, json=data, headers=headers)
    print("📩 Ответ от Whapi:", response.json())  # Логируем ответ
    return response.json()

# Обработчик входящих сообщений (вебхук)
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print("📩 Получены данные:", data)
    print("-" * 80)

    if 'messages' in data:
        print("✅ Вебхук успешно обработан")
        print("-" * 80)

        for message in data["messages"]:
            if not message["from_me"]:  # Проверяем, что сообщение не от бота
                chat_id = message["chat_id"]  # Берём chat_id
                text = message["text"]["body"]  # Достаём текст сообщения
                print("📨 Чекай текст: ", text)

                if text:
                    dialog1 = get_dialog_from_db(chat_id)
                    print(dialog1)
                    print("-" * 80)
                    if len(dialog1) >= 20:
                        del dialog1[:len(dialog1) - 20]
                    sgen_text = get_mess(text, "Ты ИИ ассистент", True, dialog1)
                    print(sgen_text)
                    print("-" * 80)
                    send_message(chat_id, sgen_text)  # Отправляем обратно тот же текст
                    dialog1.append({"role": "user", "message": text})
                    dialog1.append({"role": "assistant", "message": sgen_text})
                    print(dialog1)
                    save_dialog_to_db(chat_id, dialog1)

    return jsonify({"status": "ok"})

# Запуск сервера Flask
if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=5000)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    lt_process, tunnel_url = start_localtunnel(5000)

    # 3) Как только получили tunnel_url, шлём PATCH /settings в Whapi
    if tunnel_url:
        # Пример запроса
        API_KEY = "JeckyS6ptE9PA2ZPbq9dZD10zOMtsqOS"
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

    # 4) Оставляем приложение «жить»
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping LocalTunnel...")
        lt_process.terminate()
        lt_process.wait()