import sqlite3
import datetime
import json

conn = sqlite3.connect('dates.db', check_same_thread=False)
cursor = conn.cursor()

def createDataBase(self):

    # Создание таблицы для хранения дат, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            socialNetwork TEXT NOT NULL,
            userId TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogs (
            user_id INTEGER PRIMARY KEY,
            dialog_history TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegramChatId TEXT UNIQUE DEFAULT NULL,
            telegramUserId TEXT UNIQUE DEFAULT NULL,
            whatsappPhoneNumber TEXT UNIQUE DEFAULT NULL,
            instagramUserId TEXT UNIQUE DEFAULT NULL,
            waiting TEXT DEFAULT "False"
        )
    ''')
    conn.commit()

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

def add_user(message):
    try:
        cursor.execute(
        "INSERT INTO users (telegramChatId, telegramUserId) VALUES (?, ?)",
        (message.chat.id, message.from_user.username)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        e = e

def change_waiting_flag_true(chatId):
    cursor.execute("UPDATE users SET waiting = 'True' WHERE telegramChatId = ?", (chatId,))
    conn.commit()

def change_waiting_flag_false(chatId):
    cursor.execute("UPDATE users SET waiting = 'False' WHERE telegramChatId = ?", (chatId,))
    conn.commit()

def if_user_waiting_admin(message):
    cursor.execute("SELECT * FROM users WHERE waiting = 'True'", (message,))
    print(cursor.fetchone())
    conn.commit()

