import sqlite3
import datetime
import json
import time

def db_execute(query, params=(), commit=False, retries=5, delay=0.1):
    for attempt in range(retries):
        try:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(delay)
            else:
                raise e
    raise sqlite3.OperationalError("Database is locked after several attempts.")

conn = sqlite3.connect('dates.db', check_same_thread=False, timeout=10)
cursor = conn.cursor()
db_execute("PRAGMA busy_timeout = 5000", commit=True)

def createDataBase():
    """
    Создаёт все необходимые таблицы, если их нет.
    """
    db_execute('''
        CREATE TABLE IF NOT EXISTS dates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT
        )
    ''', commit=True)
    db_execute('''
        CREATE TABLE IF NOT EXISTS admins(
            chat_id INTEGER PRIMARY KEY UNIQUE,
            username TEXT UNIQUE
        )
    ''', commit=True)
    db_execute('''
        CREATE TABLE IF NOT EXISTS dialogs(
            user_id TEXT PRIMARY KEY,
            dialog_history TEXT
        )
    ''', commit=True)
    db_execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegramChatId TEXT UNIQUE DEFAULT NULL,
            telegramUserId TEXT UNIQUE DEFAULT NULL,
            whatsappPhoneNumber TEXT UNIQUE DEFAULT NULL,
            language TEXT DEFAULT NONE
        )
    ''', commit=True)
    # Новая таблица info: для хранения больших/длинных текстов по ключу
    db_execute('''
        CREATE TABLE IF NOT EXISTS info(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info_key TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
        )
    ''', commit=True)
    # Новая таблица QA: для хранения пар "вопрос - ответ"
    db_execute('''
        CREATE TABLE IF NOT EXISTS QA(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''', commit=True)
    db_execute('''
    CREATE TABLE IF NOT EXISTS whatsapp_admins (
        phone_number TEXT PRIMARY KEY
    )
    ''', commit=True)
    conn.commit()
def get_info_by_key(key: str):
    db_execute("SELECT content FROM info WHERE info_key = ?", (key,), commit=True)
    row = cursor.fetchone()
    return row[0] if row else None

def get_info_by_key(key:str):
    data = {
        "company_text":
        """Приветственные сообщения
- Вас приветствует AbAI.event! Фото зоны с Искусственным Интеллектом!
Задайте ваш вопрос.
- Глупые вопросы
Как дела? Как оно? Чо как? Чо каво?
Чо делаешь? Что делаешь?
Ответы:
- Как дела? Всё супер! Если хотите, могу помочь с обработкой фотографий на вашем Мероприятии. Напишите мне свой вопрос, про наши Услуги!
- Всё отлично! Сейчас работаю над крутыми фоточками для мероприятий. Вам нужна помощь в этом вопросе?

Просто первый текст при начале общения с пользователем:
Фото зоны с искусственным интеллектом на вашем мероприятии!
Наши технологии позволяют создать собственный стиль фото под ваше мероприятие.
• Зачем ждать фотографии завтра, когда можно получить их здесь и сейчас
• Подборка стиля под идею и кейс мероприятия
• Моментальная фотопечать 7-10 сек обработки фото
• Моментальное фото по QR на ваше мобильное устройство
• Полный брендинг фото зоны и программного обеспечения
Творческие решения с ИИ: мы уверены, что инновации и творчество могут объединиться для создания удивительных визуальных решений.
Минимальное время заказа - 3 часа, меньше не принимаются заказы
Стоимость: 1 час – 100 тысяч тг.
Так же изготавливаем Фото-Будки Селфи-Зеркала с ИИ под заказ
Остались вопросы?
Будем рады помочь!
Контактные данные: +7 707 33 88 591 Дияр
""",
        "company_info":
        """instagram: https://www.instagram.com/abai.event
Минимальное время заказа: 3 часа, меньше не принимаются заказы
Стоимость: 3 часа - 300 тысяч тенге
Фотобудки не продаются, только арендуются на время

Вопрос:
Предоставляются ли услуги обслуживания к вашим фотобудкам?
Ответ:
Аппарат будет обсуживаться нашим администратором который обеспечит полный комфорт и поддержку при работе с устройством. Он поможет вам быстро и удобно получить фотографии: распечатать их на месте, отправить на мобильное устройство или переслать на электронную почту. Мы позаботимся, чтобы ваш опыт был максимально простым и приятным!

Вопрос:
Полностью ли автоматизирован ваш сервис?
Ответ:
Наш сервис полностью автоматизирован и не требует вашего участия в процессе. Фото, сделанные с помощью нашего устройства, автоматически обрабатываются с использованием ИИ и преобразуются в изображения, идеально соответствующие выбранной вами тематике.
""",
        "question_text":
        """Какую информацию вы бы хотели узнать и чем я могу вам помочь
1 стили обработки ИИ
2 примеры фотографий до/после
3 рассказать информацию про деятельность нашей компании
4 преимущества нашей компании
5 что такое зона с нейросетью
6 Какие имеются фотобудки и селфи зеркала?
7 забронировать время на ваше мероприятие
8 посмотреть презентации о компании
9 посмотреть видео о компании

Ответы:
1. Стили обработки ИИ
На русском:
'Стиль обработки фото вы можете выбрать самостоятельно из списка тем...'
На казахском:
'Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу...'
На английском:
'You can choose the photo processing style yourself...'

2. Примеры фотографий до/после
На русском:
'Сейчас отправлю примеры фото с наложенным ИИ...'
... (и т.д. полный текст из question.txt)
"""
          }
    return data[key]

# *--------------------------------------------------------------------------------------------!
# *------------------------- Функции для работы whatsapp --------------------------------------!
# *--------------------------------------------------------------------------------------------!

# Функция для добавления пользователя по номеру WhatsApp (если его еще нет)
def add_whatsapp_user(phone_number):
    try:
        db_execute('INSERT INTO users (whatsappPhoneNumber) VALUES (?)', (phone_number,), commit=True)
        conn.commit()
    except sqlite3.IntegrityError:
        # Если такой пользователь уже существует, можно ничего не делать или обновить данные.
        pass

# Функция для добавления WhatsApp-админа
def add_whatsapp_admin(phone_number):
    try:
        db_execute('INSERT INTO whatsapp_admins (phone_number) VALUES (?)', (phone_number,), commit=True)
        conn.commit()
        return "Админ успешно добавлен."
    except sqlite3.IntegrityError:
        return "Админ с таким номером уже существует."


# Функция для удаления WhatsApp-админа
def delete_whatsapp_admin(phone_number):
    db_execute('DELETE FROM whatsapp_admins WHERE phone_number = ?', (phone_number,), commit=True)
    conn.commit()
    return "Админ удалён."


# Функция для получения списка номеров WhatsApp-админов
def check_whatsapp_admins():
    db_execute('SELECT phone_number FROM whatsapp_admins', commit=True)
    admins = [row[0] for row in cursor.fetchall()]
    return admins

def get_language_by_user_id_whatsapp(user_id):
    db_execute('SELECT language FROM users WHERE whatsappPhoneNumber = ?', (user_id,), commit=True)
    rows = cursor.fetchall()
    if rows:
        return rows[0][0]
    return None

def add_language_whatsapp(chat_id, language):
    db_execute('UPDATE users SET language = ? WHERE whatsappPhoneNumber = ?', (language, chat_id), commit=True)
    conn.commit()

def format_admins_table_whatsapp():
    try:
        db_execute("SELECT * FROM whatsapp_admins", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет администраторов."

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

        return f"📋 Таблица администраторов:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


# *--------------------------------------------------------------------------------------------!
# *--------------------------- Функции для работы info ----------------------------------------!
# *--------------------------------------------------------------------------------------------!

def add_info(info_key, content):
    try:
        db_execute("INSERT INTO info (info_key, content) VALUES (?, ?)", (info_key, content), commit=True)
        conn.commit()
        return f"Текст {info_key} с ответом {content} добавлен."
    except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: info.info_key" in str(e):
                return "Текст уже добавлен."
            else:
                return "Ошибка при добавлении Текста."

def delete_info(info_key):
    db_execute("SELECT * FROM info WHERE info_key = ?", (info_key,), commit=True)
    info_key = cursor.fetchone()
    if info_key:
        db_execute("DELETE FROM info WHERE info_key = ?", (info_key,), commit=True)
        conn.commit()
        return f"Текст с info_key '{info_key}' удален."
    else:
        return f"Текст с info_key '{info_key}' не найден."

def format_info_table():
    try:
        db_execute("SELECT * FROM info", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет Текстов."

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

        return f"📋 Таблица Текстов:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


# *--------------------------------------------------------------------------------------------!
# *----------------------------- Функции для работы QA ----------------------------------------!
# *--------------------------------------------------------------------------------------------!

def add_QA(question, answer):
    try:
        db_execute("INSERT INTO QA (question, answer) VALUES (?, ?)", (question, answer), commit=True)
        conn.commit()
        return f"Вопрос {question} с ответом {answer} добавлен."
    except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: QA.question" in str(e):
                return "Вопрос уже добавлен."
            else:
                return "Ошибка при добавлении вопроса."

def delete_QA(question):
    db_execute("SELECT * FROM QA WHERE question = ?", (question,), commit=True)
    question = cursor.fetchone()
    if question:
        db_execute("DELETE FROM QA WHERE question = ?", (question,), commit=True)
        conn.commit()
        return f"Вопрос с question '{question}' удален."
    else:
        return f"Вопрос с question '{question}' не найден."

def format_QA_table():
    try:
        db_execute("SELECT * FROM QA", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет вопросов и ответов."

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

        return f"📋 Таблица вопросов и ответов:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


# *--------------------------------------------------------------------------------------------!
# *--------------------------- Функции для работы admins --------------------------------------!
# *--------------------------------------------------------------------------------------------!

def add_admin(username):
    db_execute("SELECT telegramChatId FROM users WHERE telegramUserId = ?", (username,), commit=True)
    result = cursor.fetchone()
    if not result:
        return f"Пользователь с username '{username}' не найден в таблице users."
    chat_id = result[0]
    try:
        db_execute("INSERT INTO admins (chat_id, username) VALUES (?, ?)", (chat_id, username), commit=True)
        conn.commit()
        return f"Админ с username {username} и chatId {chat_id} добавлен."
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: admins.chat_id" in str(e):
            return "Админ уже добавлен."
        else:
            return "Ошибка при добавлении администратора."

def delete_admin(username):
    db_execute("SELECT * FROM admins WHERE username = ?", (username,), commit=True)
    admin = cursor.fetchone()
    if admin:
        db_execute("DELETE FROM admins WHERE username = ?", (username,), commit=True)
        conn.commit()
        return f"Админ с username '{username}' удален."
    else:
        return f"Админ с username '{username}' не найден."

def check_admins():
    db_execute("SELECT chat_id FROM admins", commit=True)
    chat_ids = [row[0] for row in cursor.fetchall()]
    db_execute("SELECT username FROM admins", commit=True)
    usernames = [row[0] for row in cursor.fetchall()]
    return [chat_ids, usernames]

def format_admins_table():
    try:
        db_execute("SELECT * FROM admins", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет администраторов."

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

        return f"📋 Таблица администраторов:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


# *--------------------------------------------------------------------------------------------!
# *---------------------------- Функции для работы dates --------------------------------------!
# *--------------------------------------------------------------------------------------------!

def save_data_to_db(date):
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        db_execute("PRAGMA table_info(dates)", commit=True)
        columns = [info[1] for info in cursor.fetchall()]

        insert_columns = ", ".join(columns[1:])
        placeholders = ", ".join(["?"] * len(columns[1:]))

        values = [formatted_date] + ['free'] * (len(columns) - 2)

        db_execute(f"INSERT INTO dates ({insert_columns}) VALUES ({placeholders})", values, commit=True)
        conn.commit()

        return "✅ Дата успешно добавлена."
    except ValueError:
        return "⚠️ Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD."
    except sqlite3.IntegrityError:
        return "⚠️ Такая дата уже существует."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def get_sorted_dates():
    db_execute("SELECT * FROM dates ORDER BY date ASC", commit=True)
    all_dates = cursor.fetchall()
    return [date[1] for date in all_dates]

def delete_date_from_db(data):
    try:
        date_obj = datetime.datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return "Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD"

    formatted_date = date_obj.strftime("%Y-%m-%d")

    db_execute("SELECT * FROM dates WHERE date = ?", (formatted_date,), commit=True)
    if cursor.fetchone() is None:
        return "Дата не найдена в базе данных."

    db_execute("DELETE FROM dates WHERE date = ?", (formatted_date,), commit=True)
    conn.commit()

    db_execute("SELECT * FROM dates WHERE date = ?", (formatted_date,), commit=True)
    if cursor.fetchone() is None:
        return "Дата успешно удалена."
    else:
        return "Не удалось удалить дату. Что-то пошло не так."

def get_all_dates_from_db():
    db_execute("SELECT * FROM dates ORDER BY date ASC", commit=True)
    rows = cursor.fetchall()
    return [date[1] for date in rows]

def add_column(column_name):
    try:
        db_execute(f"ALTER TABLE dates ADD COLUMN {column_name} TEXT DEFAULT 'free'", commit=True)
        conn.commit()
        return f"✅ Колонка '{column_name}' успешно добавлена."
    except sqlite3.OperationalError as e:
        return f"⚠️ Ошибка: {e}"

def remove_column(column_name):
    try:
        db_execute("PRAGMA table_info(dates)", commit=True)
        columns = [info[1] for info in cursor.fetchall()]

        if column_name not in columns:
            return f"⚠️ Колонка '{column_name}' не найдена."

        columns.remove(column_name)
        columns_str = ", ".join(columns)

        db_execute(f"CREATE TABLE dates_temp AS SELECT {columns_str} FROM dates", commit=True)
        conn.commit()

        db_execute("DROP TABLE dates", commit=True)
        conn.commit()

        db_execute("ALTER TABLE dates_temp RENAME TO dates", commit=True)
        conn.commit()

        return f"✅ Колонка '{column_name}' успешно удалена."
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def update_slot(date, column_name, status):
    try:
        db_execute(f"UPDATE dates SET {column_name} = ? WHERE date = ?", (status, date), commit=True)
        conn.commit()
        return f"✅ Слот '{column_name}' на дату '{date}' обновлен на '{status}'."
    except sqlite3.OperationalError as e:
        return f"⚠️ Ошибка: {e}"

def view_dates():
    db_execute("SELECT * FROM dates", commit=True)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    table = [columns] + rows
    return table

def book_slot(date, column_name):
    try:
        db_execute(f"SELECT {column_name} FROM dates WHERE date = ?", (date,), commit=True)
        status = cursor.fetchone()

        if status and status[0] == "free":
            db_execute(f"UPDATE dates SET {column_name} = 'booked' WHERE date = ?", (date,), commit=True)
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
        db_execute("SELECT * FROM dates", commit=True)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not rows:
            return "Таблица dates пуста."

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
        db_execute("SELECT * FROM dates", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В расписании нет данных."

        response = ""
        columns = [desc[0] for desc in cursor.description][2:]  # date находится в index=1

        for row in rows:
            date = row[1]
            status_values = row[2:]
            statuses = {columns[i]: status_values[i] for i in range(len(columns))}

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


# *--------------------------------------------------------------------------------------------!
# *----------------------------- Функции для работы users -------------------------------------!
# *--------------------------------------------------------------------------------------------!

def add_user(message):
    try:
        db_execute(
            "INSERT INTO users (telegramChatId, telegramUserId) VALUES (?, ?)",
            (message.chat.id, message.from_user.username), commit=True
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        # Если пользователь уже есть, ничего не делаем
        pass

def format_users_table():
    try:
        db_execute("SELECT * FROM users", commit=True)
        rows = cursor.fetchall()

        if not rows:
            return "В базе данных нет пользователей."

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

        return f"📋 Таблица пользователей:\n```\n{table}```"
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

def get_language_by_user_id(user_id):
    db_execute('SELECT language FROM users WHERE telegramChatID = ?', (user_id,), commit=True)
    rows = cursor.fetchall()
    if rows:
        return rows[0][0]
    return None

def add_language(chat_id, language):
    db_execute('UPDATE users SET language = ? WHERE telegramChatID = ?', (language, chat_id), commit=True)
    conn.commit()


# *--------------------------------------------------------------------------------------------!
# *-------------------------- Функции для работы dialogs --------------------------------------!
# *--------------------------------------------------------------------------------------------!

def get_dialog_from_db(user_id):
    db_execute("SELECT dialog_history FROM dialogs WHERE user_id = ?", (user_id,), commit=True)
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return []

def save_dialog_to_db(user_id, dialog_history):
    dialog_json = json.dumps(dialog_history)
    db_execute(
        "INSERT OR REPLACE INTO dialogs (user_id, dialog_history) VALUES (?, ?)",
        (user_id, dialog_json), commit=True
    )
    conn.commit()

def clear_dialog(user_id):
    try:
        db_execute("DELETE FROM dialogs WHERE user_id = ?", (user_id,), commit=True)
        conn.commit()
        return f"✅ Диалог для пользователя с ID {user_id} успешно очищен."
    except Exception as e:
        return f"⚠️ Ошибка при очистке диалога: {e}"