from flask import Flask, request, jsonify
import requests
from methods import *

# ДАННЫЕ ИЗ WHAPI
API_KEY = "JeckyS6ptE9PA2ZPbq9dZD10zOMtsqOS"
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
create_folders()
createDataBase()
# Инициализация Flask-приложения
app = Flask(__name__)

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
    app.run(host="0.0.0.0", port=5000, debug=True)
