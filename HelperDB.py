import sqlite3
import datetime
import json

conn = sqlite3.connect('dates.db', check_same_thread=False)
cursor = conn.cursor()

def createDataBase():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins(
            chat_id INTEGER PRIMARY KEY UNIQUE,
            username TEXT UNIQUE
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

def save_data_to_db(date):
    """Сохранение данных в базу данных SQLite, с сортировкой по дате"""
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        cursor.execute("PRAGMA table_info(dates)")
        columns = [info[1] for info in cursor.fetchall()]

        insert_columns = ", ".join(columns[1:])
        placeholders = ", ".join(["?"] * len(columns[1:]))

        values = [formatted_date] + ['free'] * (len(columns) - 2)

        cursor.execute(f"INSERT INTO dates ({insert_columns}) VALUES ({placeholders})", values)
        conn.commit()

        return "✅ Дата успешно добавлена."
    except ValueError:
        return "⚠️ Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD."
    except sqlite3.IntegrityError:
        return "⚠️ Такая дата уже существует."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


def get_sorted_dates():
    """Извлечение всех дат из базы данных, отсортированных по дате"""
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    all_dates = cursor.fetchall()
    return [date[1] for date in all_dates]


def delete_date_from_db(data):
    """Удаление даты из базы данных"""
    try:
        date_obj = datetime.datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return "Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD"

    formatted_date = date_obj.strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM dates WHERE date = ?", (formatted_date,))
    if cursor.fetchone() is None:
        return "Дата не найдена в базе данных."

    cursor.execute("DELETE FROM dates WHERE date = ?", (formatted_date,))
    conn.commit()

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
        return json.loads(row[0])
    return []

def save_dialog_to_db(user_id, dialog_history):
    """Сохранение диалога в базу данных"""
    dialog_json = json.dumps(dialog_history)
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
        cursor.execute("PRAGMA table_info(dates)")
        columns = [info[1] for info in cursor.fetchall()]

        if column_name not in columns:
            return f"⚠️ Колонка '{column_name}' не найдена."

        columns.remove(column_name)

        columns_str = ", ".join(columns)

        cursor.execute(f"CREATE TABLE dates_temp AS SELECT {columns_str} FROM dates")
        conn.commit()

        cursor.execute("DROP TABLE dates")
        conn.commit()

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
        cursor.execute("SELECT * FROM dates")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        column_widths = [max(len(str(value)) for value in [col] + [row[idx] for row in rows]) for idx, col in enumerate(columns)]

        table = "┌" + "┬".join("─" * (w + 2) for w in column_widths) + "┐\n"

        header = "│ " + " │ ".join(f"{col.ljust(column_widths[idx])}" for idx, col in enumerate(columns)) + " │\n"
        table += header

        table += "├" + "┼".join("─" * (w + 2) for w in column_widths) + "┤\n"

        for row in rows:
            row_line = "│ " + " │ ".join(f"{str(value).ljust(column_widths[idx])}" for idx, value in enumerate(row)) + " │\n"
            table += row_line

        table += "└" + "┴".join("─" * (w + 2) for w in column_widths) + "┘\n"

        return f"📋 Таблица dates:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


def check_dates_and_cabins():
    try:
        cursor.execute("SELECT * FROM dates")
        rows = cursor.fetchall()

        if not rows:
            return "В расписании нет данных."

        response = ""

        for row in rows:
            date = row[1]
            columns = [desc[0] for desc in cursor.description][2:]

            statuses = {columns[idx]: value for idx, value in enumerate(row[2:])}

            free = [k for k, v in statuses.items() if v == "free"]
            occupied = [k for k, v in statuses.items() if v != "free"]

            response += f"На {date}:\n"
            if free:
                response += f"✅ Свободны: {', '.join(free)}\n"
            if occupied:
                response += f"❌ Заняты: {', '.join(occupied)}\n"

        return response

    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def clear_dialog(user_id):
    """Удаление диалога определённого пользователя из базы данных."""
    try:
        cursor.execute("DELETE FROM dialogs WHERE user_id = ?", (user_id,))
        conn.commit()
        return f"✅ Диалог для пользователя с ID {user_id} успешно очищен."
    except Exception as e:
        return f"⚠️ Ошибка при очистке диалога: {e}"

def add_admin(username):
    cursor.execute("SELECT telegramChatId FROM users WHERE telegramUserId = ?", (username,))
    result = cursor.fetchone()
    chat_id = result[0]
    cursor.execute("INSERT INTO admins (chat_id, username) VALUES (?, ?)", (chat_id, username))
    conn.commit()
    return f"Админ с username {username} и chatId {chat_id} добавлен."

def delete_admin(username):
    cursor.execute("DELETE FROM admins WHERE username = ?", (username,))
    conn.commit()
    return f"Админ с username {username} удален."

def check_admins():
    cursor.execute("SELECT chat_id FROM admins")
    chat_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT username FROM admins")
    usernames = [row[0] for row in cursor.fetchall()]
    return [chat_ids, usernames]

def check_waiting_status(chatId):
    try:
        cursor.execute("SELECT waiting FROM users WHERE telegramChatId = ?", (chatId,))
        result = cursor.fetchone()

        waiting_status = result[0]
        if waiting_status == "True":
            return True
        else:
            return False
    except Exception as e:
        return f"⚠️ Ошибка при проверке статуса: {e}"

def format_admins_table():
    try:
        # Извлечение всех администраторов из базы данных
        cursor.execute("SELECT * FROM admins")
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет администраторов."

        columns = [desc[0] for desc in cursor.description]  # Получаем названия колонок

        # Вычисление ширины колонок для правильного отображения
        column_widths = [max(len(str(value)) for value in [col] + [row[idx] for row in rows]) for idx, col in enumerate(columns)]

        # Строим строку таблицы
        table = "┌" + "┬".join("─" * (w + 2) for w in column_widths) + "┐\n"

        # Добавляем заголовок
        header = "│ " + " │ ".join(f"{col.ljust(column_widths[idx])}" for idx, col in enumerate(columns)) + " │\n"
        table += header

        # Добавляем разделительную линию
        table += "├" + "┼".join("─" * (w + 2) for w in column_widths) + "┤\n"

        # Добавляем строки данных
        for row in rows:
            row_line = "│ " + " │ ".join(f"{str(value).ljust(column_widths[idx])}" for idx, value in enumerate(row)) + " │\n"
            table += row_line

        # Добавляем нижнюю границу таблицы
        table += "└" + "┴".join("─" * (w + 2) for w in column_widths) + "┘\n"

        return f"📋 Таблица администраторов:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def format_users_table():
    try:
        # Извлечение всех пользователей из базы данных
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет пользователей."

        columns = [desc[0] for desc in cursor.description]  # Получаем названия колонок

        # Вычисление ширины колонок для правильного отображения
        column_widths = [max(len(str(value)) for value in [col] + [row[idx] for row in rows]) for idx, col in enumerate(columns)]

        # Строим строку таблицы
        table = "┌" + "┬".join("─" * (w + 2) for w in column_widths) + "┐\n"

        # Добавляем заголовок
        header = "│ " + " │ ".join(f"{col.ljust(column_widths[idx])}" for idx, col in enumerate(columns)) + " │\n"
        table += header

        # Добавляем разделительную линию
        table += "├" + "┼".join("─" * (w + 2) for w in column_widths) + "┤\n"

        # Добавляем строки данных
        for row in rows:
            row_line = "│ " + " │ ".join(f"{str(value).ljust(column_widths[idx])}" for idx, value in enumerate(row)) + " │\n"
            table += row_line

        # Добавляем нижнюю границу таблицы
        table += "└" + "┴".join("─" * (w + 2) for w in column_widths) + "┘\n"

        return f"📋 Таблица пользователей:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"
