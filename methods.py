import requests
import json
import sqlite3
from datetime import datetime

# Подключение к базе данных
conn = sqlite3.connect('dates.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы для хранения дат, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dialogs (
        user_id INTEGER,
        dialog_history TEXT,
        PRIMARY KEY (user_id)
    )
''')
conn.commit()



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


def save_data_to_db(data):
    """Сохранение данных в базу данных SQLite, с сортировкой по дате"""
    try:
        # Преобразуем строку в объект даты
        date_obj = datetime.strptime(data, "%Y-%m-%d")  # Ожидаемый формат: YYYY-MM-DD
    except ValueError:
        return "Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD"

    # Преобразуем обратно в строку в формате YYYY-MM-DD для записи в базу
    formatted_date = date_obj.strftime("%Y-%m-%d")

    # Добавляем дату в таблицу
    cursor.execute("INSERT INTO dates (date) VALUES (?)", (formatted_date,))
    conn.commit()

    # Теперь извлекаем все даты из базы, отсортированные по дате
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    all_dates = cursor.fetchall()

    # Возвращаем отсортированный список дат
    return [date[1] for date in all_dates]


def get_sorted_dates():
    """Извлечение всех дат из базы данных, отсортированных по дате"""
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    all_dates = cursor.fetchall()
    return [date[1] for date in all_dates]


def delete_date_from_db(data):
    """Удаление даты из базы данных"""
    try:
        # Преобразуем строку в объект даты
        date_obj = datetime.strptime(data, "%Y-%m-%d")  # Ожидаемый формат: YYYY-MM-DD
    except ValueError:
        return "Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD"

    # Преобразуем обратно в строку в формате YYYY-MM-DD для удаления из базы
    formatted_date = date_obj.strftime("%Y-%m-%d")

    # Проверяем, существует ли дата в базе
    cursor.execute("SELECT * FROM dates WHERE date = ?", (formatted_date,))
    if cursor.fetchone() is None:
        return "Дата не найдена в базе данных."

    # Удаляем дату из базы
    cursor.execute("DELETE FROM dates WHERE date = ?", (formatted_date,))
    conn.commit()

    # Проверим, была ли дата удалена
    cursor.execute("SELECT * FROM dates WHERE date = ?", (formatted_date,))
    if cursor.fetchone() is None:
        return "Дата успешно удалена."
    else:
        return "Не удалось удалить дату. Что-то пошло не так."

def get_all_dates_from_db():
    """Извлечение всех дат из базы данных, отсортированных по дате"""
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    rows = cursor.fetchall()
    return [date[1] for date in rows]

def get_dialog_from_db(user_id):
    """Извлечение диалога для указанного пользователя"""
    cursor.execute("SELECT dialog_history FROM dialogs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])  # Преобразование из JSON
    return []

def save_dialog_to_db(user_id, dialog_history):
    """Сохранение диалога в базу данных"""
    dialog_json = json.dumps(dialog_history)  # Преобразование в JSON
    cursor.execute(
        "INSERT OR REPLACE INTO dialogs (user_id, dialog_history) VALUES (?, ?)",
        (user_id, dialog_json)
    )
    conn.commit()

def getDateAndTime(self):
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")