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
            date TEXT
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
        date_obj = datetime.datetime.strptime(data, "%Y-%m-%d")  # Ожидаемый формат: YYYY-MM-DD
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

def get_waiting_users():
    cursor.execute("SELECT telegramChatId FROM users WHERE waiting = 'True'")
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def add_column(column_name):
    try:
        cursor.execute(f"ALTER TABLE dates ADD COLUMN {column_name} TEXT DEFAULT 'free'")
        conn.commit()
        return f"✅ Колонка '{column_name}' успешно добавлена."
    except sqlite3.OperationalError as e:
        return f"⚠️ Ошибка: {e}"

def remove_column(column_name):
    try:
        # Получаем список всех колонок в таблице
        cursor.execute("PRAGMA table_info(dates)")
        columns = [info[1] for info in cursor.fetchall()]

        if column_name not in columns:
            return f"⚠️ Колонка '{column_name}' не найдена."

        # Создаем новый список колонок, исключив из него колонку, которую нужно удалить
        columns.remove(column_name)

        # Формируем строку с колонками для новой таблицы
        columns_str = ", ".join(columns)

        # Создаем новую временную таблицу с нужными колонками
        cursor.execute(f"CREATE TABLE dates_temp AS SELECT {columns_str} FROM dates")
        conn.commit()

        # Удаляем старую таблицу
        cursor.execute("DROP TABLE dates")
        conn.commit()

        # Переименовываем временную таблицу в оригинальное имя
        cursor.execute("ALTER TABLE dates_temp RENAME TO dates")
        conn.commit()

        return f"✅ Колонка '{column_name}' успешно удалена."

    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def update_slot(date, column_name, status):
    try:
        cursor.execute(f"UPDATE dates SET {column_name} = ? WHERE date = ?", (status, date))
        conn.commit()
        return f"✅ Слот '{column_name}' на дату '{date}' обновлен на '{status}'."
    except sqlite3.OperationalError as e:
        return f"⚠️ Ошибка: {e}"

def view_dates():
    cursor.execute("SELECT * FROM dates")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    table = [columns] + rows
    return table

def book_slot(date, column_name):
    try:
        cursor.execute(f"SELECT {column_name} FROM dates WHERE date = ?", (date,))
        status = cursor.fetchone()

        if status and status[0] == "free":
            cursor.execute(f"UPDATE dates SET {column_name} = 'booked' WHERE date = ?", (date,))
            conn.commit()
            return f"✅ Слот '{column_name}' на дату '{date}' успешно забронирован."
        elif status:
            return f"⚠️ Слот '{column_name}' на дату '{date}' уже занят."
        else:
            return f"⚠️ Дата '{date}' не найдена."
    except sqlite3.OperationalError as e:
        return f"⚠️ Ошибка: {e}"

def format_table():
    try:
        # Получаем данные из таблицы
        cursor.execute("SELECT * FROM dates")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Определяем ширину колонок для выравнивания
        column_widths = [max(len(str(value)) for value in [col] + [row[idx] for row in rows]) for idx, col in enumerate(columns)]

        # Формируем верхнюю границу таблицы
        table = "┌" + "┬".join("─" * (w + 2) for w in column_widths) + "┐\n"

        # Формируем заголовок таблицы
        header = "│ " + " │ ".join(f"{col.ljust(column_widths[idx])}" for idx, col in enumerate(columns)) + " │\n"
        table += header

        # Добавляем разделитель между заголовком и данными
        table += "├" + "┼".join("─" * (w + 2) for w in column_widths) + "┤\n"

        # Формируем строки данных
        for row in rows:
            row_line = "│ " + " │ ".join(f"{str(value).ljust(column_widths[idx])}" for idx, value in enumerate(row)) + " │\n"
            table += row_line

        # Формируем нижнюю границу таблицы
        table += "└" + "┴".join("─" * (w + 2) for w in column_widths) + "┘\n"

        # Возвращаем результат в формате для Telegram
        return f"📋 Таблица dates:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


def check_dates_and_cabins():
    try:
        # Получаем все записи из таблицы dates
        cursor.execute("SELECT * FROM dates")
        rows = cursor.fetchall()

        if not rows:
            return "В расписании нет данных."

        # Составляем список для формулировки ответа
        response = ""

        for row in rows:
            date = row[1]  # Предположим, что дата вторая колонка (индекс 1)
            columns = [desc[0] for desc in cursor.description][2:]  # Пропускаем `id` и `date`

            # Статусы кабинок для текущей даты
            statuses = {columns[idx]: value for idx, value in enumerate(row[2:])}

            free = [k for k, v in statuses.items() if v == "free"]
            occupied = [k for k, v in statuses.items() if v != "free"]

            # Формируем ответ для текущей даты
            response += f"На {date}:\n"
            if free:
                response += f"✅ Свободны: {', '.join(free)}\n"
            if occupied:
                response += f"❌ Заняты: {', '.join(occupied)}\n"

        return response

    except Exception as e:
        return f"⚠️ Ошибка: {e}"