import sqlite3
import datetime
import json

conn = sqlite3.connect('dates.db', check_same_thread=False)
cursor = conn.cursor()

def get_info_by_key(key: str):
    cursor.execute("SELECT content FROM info WHERE info_key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def createDataBase():
    """
    Создаёт все необходимые таблицы, если их нет.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates(
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
        CREATE TABLE IF NOT EXISTS dialogs(
            user_id TEXT PRIMARY KEY,
            dialog_history TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegramChatId TEXT UNIQUE DEFAULT NULL,
            telegramUserId TEXT UNIQUE DEFAULT NULL,
            whatsappPhoneNumber TEXT UNIQUE DEFAULT NULL,
            language TEXT DEFAULT NONE
        )
    ''')
    # Новая таблица info: для хранения больших/длинных текстов по ключу
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info_key TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    # Новая таблица QA: для хранения пар "вопрос - ответ"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS QA(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Если хотите, можете здесь же один раз заполнить таблицы:
    # fill_info_table()
    # fill_qa_table()

def fill_info_table():
    """
    Заполняет таблицу info текстами, которые раньше были в text.txt, company_info.txt, question.txt.
    Вызывается один раз (или по необходимости), чтобы заполнить базу.
    """
    data = [
        # Вместо text.txt
        (
            "company_text",
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
"""
        ),
        # Вместо company_info.txt
        (
            "company_info",
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
"""
        ),
        # Вместо question.txt
        (
            "question_text",
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
        )
    ]
    #for info_key, content in data:
        #cursor.execute('''
        #    INSERT OR REPLACE INTO info (info_key, content) VALUES (?, ?)
        #''', (info_key, content))
    #conn.commit()
    #print("Таблица info заполнена данными.")


# !--------------------------------------------------------------------------------------------!
# !--------------------------- Функции для работы info ----------------------------------------!
# !--------------------------------------------------------------------------------------------!

def add_info(info_key, content):
    try:
        cursor.execute("INSERT INTO info (info_key, content) VALUES (?, ?)", (info_key, content))
        conn.commit()
        return f"Текст {info_key} с ответом {content} добавлен."
    except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: info.info_key" in str(e):
                return "Текст уже добавлен."
            else:
                return "Ошибка при добавлении Текста."

def delete_info(info_key):
    cursor.execute("SELECT * FROM info WHERE info_key = ?", (info_key,))
    info_key = cursor.fetchone()
    if info_key:
        cursor.execute("DELETE FROM info WHERE info_key = ?", (info_key,))
        conn.commit()
        return f"Текст с info_key '{info_key}' удален."
    else:
        return f"Текст с info_key '{info_key}' не найден."

def format_info_table():
    try:
        cursor.execute("SELECT * FROM info")
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


# !--------------------------------------------------------------------------------------------!
# !----------------------------- Функции для работы QA ----------------------------------------!
# !--------------------------------------------------------------------------------------------!

def add_QA(question, answer):
    try:
        cursor.execute("INSERT INTO QA (question, answer) VALUES (?, ?)", (question, answer))
        conn.commit()
        return f"Вопрос {question} с ответом {answer} добавлен."
    except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: QA.question" in str(e):
                return "Вопрос уже добавлен."
            else:
                return "Ошибка при добавлении вопроса."

def delete_QA(question):
    cursor.execute("SELECT * FROM QA WHERE question = ?", (question,))
    question = cursor.fetchone()
    if question:
        cursor.execute("DELETE FROM QA WHERE question = ?", (question,))
        conn.commit()
        return f"Вопрос с question '{question}' удален."
    else:
        return f"Вопрос с question '{question}' не найден."

def format_QA_table():
    try:
        cursor.execute("SELECT * FROM QA")
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


# !--------------------------------------------------------------------------------------------!
# !--------------------------- Функции для работы admins --------------------------------------!
# !--------------------------------------------------------------------------------------------!

def add_admin(username):
    cursor.execute("SELECT telegramChatId FROM users WHERE telegramUserId = ?", (username,))
    result = cursor.fetchone()
    if not result:
        return f"Пользователь с username '{username}' не найден в таблице users."
    chat_id = result[0]
    try:
        cursor.execute("INSERT INTO admins (chat_id, username) VALUES (?, ?)", (chat_id, username))
        conn.commit()
        return f"Админ с username {username} и chatId {chat_id} добавлен."
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: admins.chat_id" in str(e):
            return "Админ уже добавлен."
        else:
            return "Ошибка при добавлении администратора."

def delete_admin(username):
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = cursor.fetchone()
    if admin:
        cursor.execute("DELETE FROM admins WHERE username = ?", (username,))
        conn.commit()
        return f"Админ с username '{username}' удален."
    else:
        return f"Админ с username '{username}' не найден."

def check_admins():
    cursor.execute("SELECT chat_id FROM admins")
    chat_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT username FROM admins")
    usernames = [row[0] for row in cursor.fetchall()]
    return [chat_ids, usernames]

def format_admins_table():
    try:
        cursor.execute("SELECT * FROM admins")
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


# !--------------------------------------------------------------------------------------------!
# !---------------------------- Функции для работы dates --------------------------------------!
# !--------------------------------------------------------------------------------------------!

def save_data_to_db(date):
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
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    all_dates = cursor.fetchall()
    return [date[1] for date in all_dates]

def delete_date_from_db(data):
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
    cursor.execute("SELECT * FROM dates ORDER BY date ASC")
    rows = cursor.fetchall()
    return [date[1] for date in rows]

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
        cursor.execute("SELECT * FROM dates")
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


# !--------------------------------------------------------------------------------------------!
# !----------------------------- Функции для работы users -------------------------------------!
# !--------------------------------------------------------------------------------------------!

def add_user(message):
    try:
        cursor.execute(
            "INSERT INTO users (telegramChatId, telegramUserId) VALUES (?, ?)",
            (message.chat.id, message.from_user.username)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        # Если пользователь уже есть, ничего не делаем
        pass

def format_users_table():
    try:
        cursor.execute("SELECT * FROM users")
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
    cursor.execute('SELECT language FROM users WHERE telegramChatID = ?', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return rows[0][0]
    return None

def add_language(chat_id, language):
    cursor.execute('UPDATE users SET language = ? WHERE telegramChatID = ?', (language, chat_id))
    conn.commit()


# !--------------------------------------------------------------------------------------------!
# !-------------------------- Функции для работы dialogs --------------------------------------!
# !--------------------------------------------------------------------------------------------!

def get_dialog_from_db(user_id):
    cursor.execute("SELECT dialog_history FROM dialogs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return []

def save_dialog_to_db(user_id, dialog_history):
    dialog_json = json.dumps(dialog_history)
    cursor.execute(
        "INSERT OR REPLACE INTO dialogs (user_id, dialog_history) VALUES (?, ?)",
        (user_id, dialog_json)
    )
    conn.commit()

def clear_dialog(user_id):
    try:
        cursor.execute("DELETE FROM dialogs WHERE user_id = ?", (user_id,))
        conn.commit()
        return f"✅ Диалог для пользователя с ID {user_id} успешно очищен."
    except Exception as e:
        return f"⚠️ Ошибка при очистке диалога: {e}"