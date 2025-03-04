# -*- coding: utf-8 -*-
import telebot
import os
from methods2 import *
from HelperDB2 import *
from datetime import datetime

# Создаём папки, базу данных и (при желании) наполняем её
create_folders()
createDataBase()
# fill_info_table()   # <-- раскомментируйте при первом запуске, чтобы заполнить таблицу info
# fill_qa_table()     # <-- раскомментируйте, если нужно заполнить таблицу QA

bot = telebot.TeleBot("7947945450:AAHOqe3od-WjvsnHeBb_TcQol7iVLFcahJA")

info_about_commands = (
    "Информация о командах:\n"
    #
    "!пользователи\n"
    "!команды\n"
    "!очистить-историю-диалога\n"
    #
    "!вопросы-ответы\n"
    "!удалить-вопрос-ответ\n"
    "!добавить-вопрос-ответ\n"
    #
    "!информация\n"
    "!удалить-информацию\n"
    "!добавить-информацию\n"
    "!добавить-данные-о-кабинках\n"
    #
    "!админы\n"
    "!удалить-админа\n"
    "!добавить-админа\n"
    #
    "!добавить-колонку\n"
    "!удалить-колонку\n"
    "!обновить-бронь-даты\n"
    "!показать-таблицу\n"
    "!забронировать\n"
    "!добавить-дату\n"
    "!удалить-дату\n"
    #
    "!добавить-папку\n"
    "!удалить-папку\n"
    "!добавить-файл\n"
    "!удалить-файл"
)

# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа общие ---------------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!пользователи') and message.from_user.username in check_admins()[1])
def handle_show_users(message):
    formatted_table = format_users_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!команды') and message.from_user.username in check_admins()[1])
def handle_show_commands(message):
    bot.send_message(message.chat.id, info_about_commands)

@bot.message_handler(func=lambda message: message.text.startswith('!очистить-историю-диалога'))
def handle_clear_history(message):
    try:
        chatID = message.text.split(" ", 1)[1]
        if chatID == "мою":
            result = clear_dialog(message.chat.id)
        else:
            result = clear_dialog(int(chatID))
    except Exception:
        result = "⚠️ Введите существующий chat ID"
    bot.reply_to(message, result)


# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа вопросы-ответы ------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!вопросы-ответы') and message.from_user.username in check_admins()[1])
def handle_show_QA(message):
    formatted_table = format_QA_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-вопрос-ответ') and message.from_user.username in check_admins()[1])
def handle_delete_QA_cmd(message):
    try:
        QA = message.text.split(" ", 1)[1]
        result = delete_QA(QA)
    except Exception:
        result = "⚠️ Не получилось удалить вопрос-ответ."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-вопрос-ответ') and message.from_user.username in check_admins()[1])
def handle_add_QA_cmd(message):
    try:
        # Убираем саму команду, получаем текст после неё
        text_after_command = message.text[len('!добавить-вопрос-ответ'):].strip()
        # Пример: "?Как дела? !Всё супер!"

        # Разделим по первому вхождению "!" (т.к. ответ начинается после '!'):
        splitted = text_after_command.split('!', 1)
        if len(splitted) < 2:
            bot.reply_to(message, "⚠️ Неверный формат. Пример: !добавить-вопрос-ответ ?Как дела? !Всё супер!")
            return

        question_part = splitted[0].strip()   # допустим "?Как дела?"
        answer_part = splitted[1].strip()     # допустим "Всё супер!"

        # Удалим ведущий "?" у вопроса, если он есть
        if question_part.startswith('?'):
            question_part = question_part[1:].strip()

        # Теперь добавляем в БД
        result = add_QA(question_part, answer_part)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"Ошибка при добавлении вопроса-ответа: {e}")


# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа информация ----------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!информация') and message.from_user.username in check_admins()[1])
def handle_show_info(message):
    formatted_table = format_info_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-информацию') and message.from_user.username in check_admins()[1])
def handle_delete_info_cmd(message):
    try:
        text = message.text.split(" ", 1)[1]
        result = delete_info(text)
    except Exception:
        result = "⚠️ Не получилось удалить информацию."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-информацию') and message.from_user.username in check_admins()[1])
def handle_add_info_cmd(message):
    try:
        # Убираем саму команду, получаем текст после неё
        text_after_command = message.text[len('!добавить-информацию'):].strip()
        # Пример: "?Как дела? !Всё супер!"

        # Разделим по первому вхождению "!" (т.к. ответ начинается после '!'):
        splitted = text_after_command.split('!', 1)
        if len(splitted) < 2:
            bot.reply_to(message, "⚠️ Неверный формат. Пример: !инфмормацию ?ключ !контент")
            return

        info_key = splitted[0].strip()   # допустим "?Как дела?"
        content = splitted[1].strip()     # допустим "Всё супер!"

        # Удалим ведущий "?" у вопроса, если он есть
        if info.startswith('?'):
            info = info[1:].strip()

        # Теперь добавляем в БД
        result = add_QA(info, content)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"Ошибка при добавлении информации: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-данные-о-кабинках') and message.from_user.username in check_admins()[1])
def handle_add_cabins(message):
    # В исходном коде вы писали "write_file('cabins', message.text)",
    # Но теперь вы хотите всё хранить в БД. Можете завести отдельную таблицу, аналогично QA,
    # или хранить в info по ключу "cabins_info". Здесь – как пример:
    if message.from_user.username in check_admins()[1]:
        bot.send_message(message.chat.id, "Введите информацию о кабинках.")
        bot.register_next_step_handler(message, add_cabin_info)

def add_cabin_info(message):
    new_text = message.text
    # Например, запишем в таблицу info под ключом "cabins_info"
    from HelperDB import cursor, conn
    cursor.execute('INSERT OR REPLACE INTO info (info_key, content) VALUES (?, ?)', ("cabins_info", new_text))
    conn.commit()
    bot.send_message(message.chat.id, "Информация о кабинках сохранена в БД под ключом 'cabins_info'.")


# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа админы --------------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!админы') and message.from_user.username in check_admins()[1])
def handle_show_admins(message):
    formatted_table = format_admins_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-админа') and message.from_user.username in check_admins()[1])
def handle_delete_admin_cmd(message):
    try:
        username = message.text.split(" ", 1)[1]
        result = delete_admin(username)
    except Exception:
        result = "⚠️ Не получилось удалить админа."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-админа') and message.from_user.username in check_admins()[1])
def handle_add_admin_cmd(message):
    try:
        username = message.text.split(" ", 1)[1]
        result = add_admin(username)
    except Exception as e:
        print(f"Error: {e}")
        result = "⚠️ Не получилось добавить админа."
    bot.reply_to(message, result)


# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа даты ----------------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-колонку') and message.from_user.username in check_admins()[1])
def handle_add_column_cmd(message):
    try:
        column_name = message.text.split(" ", 1)[1]
        result = add_column(column_name)
    except IndexError:
        result = "⚠️ Используйте: !добавить-колонку <название_продолжение>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-колонку') and message.from_user.username in check_admins()[1])
def handle_remove_column_cmd(message):
    try:
        column_name = message.text.split(" ", 1)[1]
        result = remove_column(column_name)
    except IndexError:
        result = "⚠️ Используйте: !удалить-колонку <название_продолжение>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!обновить-бронь-даты') and message.from_user.username in check_admins()[1])
def handle_update_slot_cmd(message):
    try:
        if message.text == "выйти":
            bot.send_message(message.chat.id, "Выхожу из функции.")
            return
        _, date_str, column_name, status = message.text.split(" ", 3)
        if status not in ["free", "booked"]:
            bot.send_message(message.chat.id, "В качестве статуса используйте <free> или <booked>")
            bot.register_next_step_handler(message, handle_update_slot_cmd)
            return
        result = update_slot(date_str, column_name, status)
    except ValueError:
        result = "⚠️ Используйте: !обновить-бронь-даты <дата> <колонка> <статус>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!показать-таблицу') and message.from_user.username in check_admins()[1])
def handle_view_dates(message):
    formatted_table = format_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!забронировать') and message.from_user.username in check_admins()[1])
def handle_book_slot_cmd(message):
    try:
        _, date_str, column_name = message.text.split(" ", 2)
        result = book_slot(date_str, column_name)
    except ValueError:
        result = "⚠️ Используйте: !забронировать <дата> <колонка>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-дату') and message.from_user.username in check_admins()[1])
def handle_add_date_cmd(message):
    data = message.text[len('!добавить-дату '):].strip()
    if data:
        result = save_data_to_db(data)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Не была указана дата. Пожалуйста, введите её.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-дату') and message.from_user.username in check_admins()[1])
def handle_delete_date_cmd(message):
    data = message.text[len('!удалить-дату '):].strip()
    if data:
        result = delete_date_from_db(data)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Не была указана дата для удаления. Пожалуйста, введите её.")


# *--------------------------------------------------------------------------------------------!
# *--------------------- Слушатели для типа файлы ---------------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-папку'))
def handle_add_folder(message):
    bot.send_message(message.chat.id, f"Укажите папку, в которой вы хотите создать новую папку.\n{display_files()}")
    bot.register_next_step_handler(message, process_add_folder, os.getcwd())

def process_add_folder(message, current_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        target_path = os.path.join(current_path, message.text)
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            bot.send_message(message.chat.id, "Введите корректное название папки или напишите <Выйти>.")
            bot.register_next_step_handler(message, process_add_folder, current_path)
            return

        bot.send_message(message.chat.id, "Введите название новой папки, которую хотите создать, или напишите <Выйти>.")
        bot.register_next_step_handler(message, create_folder, target_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при добавлении папки: {e}")

def create_folder(message, folder_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        new_folder_name = message.text.strip()
        new_folder_path = os.path.join(folder_path, new_folder_name)

        if os.path.exists(new_folder_path):
            bot.send_message(message.chat.id, "Папка с таким названием уже существует. Попробуйте снова или напишите <Выйти>.")
            bot.register_next_step_handler(message, create_folder, folder_path)
        else:
            os.makedirs(new_folder_path)
            bot.send_message(message.chat.id, f"Папка '{new_folder_name}' успешно создана в '{folder_path}'.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при создании папки: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-папку'))
def handle_delete_folder(message):
    bot.send_message(message.chat.id, f"Укажите папку, в которой вы хотите удалить папку.\n{display_files()}")
    bot.register_next_step_handler(message, process_delete_folder, os.getcwd())

def process_delete_folder(message, current_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        target_path = os.path.join(current_path, message.text)
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            bot.send_message(message.chat.id, "Введите корректное название папки или напишите <Выйти>.")
            bot.register_next_step_handler(message, process_delete_folder, current_path)
            return

        check = check_folder_contents(target_path)
        bot.send_message(message.chat.id, check[0])

        if check[1]:  # Есть подпапки
            bot.send_message(message.chat.id, "Укажите название подпапки, которую хотите удалить, или напишите <Выйти>.")
            bot.register_next_step_handler(message, confirm_delete_folder, target_path)
        else:
            bot.send_message(message.chat.id, "Введите название подпапки, которую хотите удалить, или напишите <Выйти>.")
            bot.register_next_step_handler(message, confirm_delete_folder, target_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении папки: {e}")

def confirm_delete_folder(message, folder_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        folder_name = message.text.strip()
        target_folder_path = os.path.join(folder_path, folder_name)

        if os.path.exists(target_folder_path) and os.path.isdir(target_folder_path):
            contents = os.listdir(target_folder_path)
            if contents:
                bot.send_message(message.chat.id, f"В папке '{folder_name}' есть файлы или подпапки. Вы уверены, что хотите удалить её? (да/нет)")
                bot.register_next_step_handler(message, delete_folder_with_confirmation, target_folder_path)
            else:
                os.rmdir(target_folder_path)
                bot.send_message(message.chat.id, f"Папка '{folder_name}' успешно удалена.")
        else:
            bot.send_message(message.chat.id, "Папка с таким названием не найдена. Попробуйте снова или напишите <Выйти>.")
            bot.register_next_step_handler(message, confirm_delete_folder, folder_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при проверке папки: {e}")

def delete_folder_with_confirmation(message, folder_path):
    try:
        if message.text.lower() == "да":
            # Удаляем содержимое папки и саму папку
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    delete_folder_contents(item_path)
            os.rmdir(folder_path)
            bot.send_message(message.chat.id, f"Папка '{os.path.basename(folder_path)}' и её содержимое успешно удалены.")
        elif message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Удаление отменено.")
        else:
            bot.send_message(message.chat.id, "Введите 'да' или 'нет'.")
            bot.register_next_step_handler(message, delete_folder_with_confirmation, folder_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении папки: {e}")

def delete_folder_contents(folder_path):
    """Рекурсивно удаляет содержимое папки."""
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            delete_folder_contents(item_path)
    os.rmdir(folder_path)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-файл'))
def handle_add_file(message):
    bot.send_message(message.chat.id, f"Укажите в какую папку вы хотите добавить файл.\n{display_files()}")
    bot.register_next_step_handler(message, process_file, os.getcwd())

def process_file(message, current_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        target_path = os.path.join(current_path, message.text)
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            bot.send_message(message.chat.id, "Введите корректное название папки или напишите <Выйти>.")
            bot.register_next_step_handler(message, process_file, current_path)
            return

        check = check_folder_contents(target_path)
        bot.send_message(message.chat.id, check[0])

        if not check[1] and not check[2]:
            bot.send_message(message.chat.id, "Можете отправить файл, и я добавлю его в данную папку.")
            bot.register_next_step_handler(message, save_file, target_path)
        elif check[1] and check[2] is None:
            bot.register_next_step_handler(message, process_file, target_path)
        elif not check[1] and check[2]:
            bot.send_message(message.chat.id, "Можете отправить файл, и я добавлю его в данную папку или напишите <Выйти>.")
            bot.register_next_step_handler(message, save_file, target_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке папки: {e}")

def save_file(message, folder_path):
    try:
        if message.text and message.text.lower() == 'выйти':
            bot.send_message(message.chat.id, 'Выхожу из функции.')
            return

        if message.document or message.photo or message.video:
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                original_name = message.document.file_name
            elif message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)
                original_name = "photo.jpg"
            elif message.video:
                file_info = bot.get_file(message.video.file_id)
                original_name = "video.mp4"
            downloaded_file = bot.download_file(file_info.file_path)

            bot.send_message(message.chat.id, "Введите название файла без расширения:")
            bot.register_next_step_handler(message, save_file_with_custom_name, folder_path, downloaded_file, original_name)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте документ, фото или видео.")
            bot.register_next_step_handler(message, save_file, folder_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении файла: {e}")

def save_file_with_custom_name(message, folder_path, file_data, original_name):
    try:
        custom_name = message.text.strip()
        if not custom_name:
            bot.send_message(message.chat.id, "Название файла не может быть пустым. Попробуйте снова.")
            bot.register_next_step_handler(message, save_file_with_custom_name, folder_path, file_data, original_name)
            return

        file_extension = os.path.splitext(original_name)[1]
        final_name = f"{custom_name}{file_extension}"
        file_path = os.path.join(folder_path, final_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(file_data)

        bot.send_message(message.chat.id, f"Файл '{final_name}' успешно сохранен в папке '{folder_path}'.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении файла: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл'))
def handle_delete_file(message):
    bot.send_message(message.chat.id, f"Укажите папку, в которой вы хотите удалить файл.\n{display_files()}")
    bot.register_next_step_handler(message, process_delete_file, os.getcwd())

def process_delete_file(message, current_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        target_path = os.path.join(current_path, message.text)
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            bot.send_message(message.chat.id, "Введите корректное название папки или напишите <Выйти>.")
            bot.register_next_step_handler(message, process_delete_file, current_path)
            return

        check = check_folder_contents(target_path)
        bot.send_message(message.chat.id, check[0])

        if not check[1] and not check[2]:
            bot.send_message(message.chat.id, "В данной папке нет файлов для удаления.")
            return
        elif not check[1] and check[2]:
            bot.send_message(message.chat.id, "Укажите название файла, который вы хотите удалить, или напишите <Выйти>.")
            bot.register_next_step_handler(message, delete_file, target_path)
        elif check[1] and check[2] is None:
            bot.send_message(message.chat.id, "В данной папке нет файлов, но есть подпапки. Укажите, в какую вы хотите перейти:")
            bot.register_next_step_handler(message, process_delete_file, target_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке папки: {e}")

def delete_file(message, folder_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        file_name = message.text.strip()
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            bot.send_message(message.chat.id, f"Файл '{file_name}' успешно удален из папки '{folder_path}'.")
        else:
            bot.send_message(message.chat.id, "Файл с таким названием не найден. Попробуйте снова или напишите <Выйти>.")
            bot.register_next_step_handler(message, delete_file, folder_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении файла: {e}")


# *--------------------------------------------------------------------------------------------!
# *------------------------- Слушатели для текста ---------------------------------------------!
# *--------------------------------------------------------------------------------------------!

@bot.message_handler(content_types=["text"])
def welcome(message):
    add_user(message)
    try:
        print(message)
        # Если сообщение не начинается с '!'
        if not message.text.startswith('!'):
            dialog = get_dialog_from_db(message.chat.id)
            # Оставляем только последние 20 сообщений
            if len(dialog) >= 20:
                del dialog[:len(dialog) - 20]

            all_dates = get_all_dates_from_db()
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            print(get_language_by_user_id(message.chat.id))

            if get_language_by_user_id(message.chat.id) == "NONE":
                print("Нету языка")
                prompt = (
                    "Ты искусственный помощник техподдержки компании 'AbAi event', но у пользователя не установлен язык. "
                    "Спроси: 'Выберите язык для удобного взаимодействия:\n"
                    " - Қазақша 🇰🇿\n - Русский 🇷🇺\n - English 🇬🇧'\n"
                    "При выборе языка отправь: 'Смена языка на <название языка>, Тілді қазақ тіліне ауыстыру, Switching language to <название языка>.'"
                )
                sgen_text = get_mess(message.text, prompt, True, dialog)
            else:
                prompt = (
                    f"Ты – помощник техподдержки компании 'AbAi event'. Отвечай только по теме: компания, бронь или диалог, "
                    f"используя язык пользователя, и добавляй эмодзи ко всему тексту (при перечислении — эмодзи перед каждой строкой).\n\n"
                    f"Язык пользователя: {get_language_by_user_id(message.chat.id)}.\n"

                    f"📅 **Бронирование:**\n"
                    f"• Проверь дату: {getDateAndTime(message)}.\n"
                    f"• Используй данные: {check_dates_and_cabins()}. Если дата отсутствует — брони нет, а свободные кабинки отправляй списком.\n\n"
                    
                    f"🏢 **Информация о компании:**\n"
                    f"• **Основной текст:**\n"
                    f"🎉 Приветствие от AbAI.event!\n"
                    f"Добро пожаловать в мир фото зон с Искусственным Интеллектом!\n\n"
                    f"❓ Задайте свой вопрос, мы всегда рады помочь!\n\n"
                    f"🙃 Некоторые неуместные вопросы (например, \"Как дела?\" или \"Что делаешь?\") можно игнорировать.\n"
                    f"👉 Ответы:\n"
                    f"   • \"Всё супер! Готов помочь с обработкой фотографий для вашего мероприятия. Задайте, пожалуйста, вопрос по нашим услугам.\"\n"
                    f"   • \"Всё отлично! Сейчас работаю над крутыми фотоснимками. Чем могу помочь?\"\n\n"
                    f"📸 **Основное сообщение:**\n"
                    f"Фото зона с ИИ для вашего мероприятия! Наши технологии позволяют создать уникальный стиль фото под вашу идею:\n"
                    f"   • Зачем ждать фотографии завтра, если можно получить их уже сейчас?\n"
                    f"   • Индивидуальный подбор стиля для вашего кейса\n"
                    f"   • Моментальная обработка и печать (7–10 сек)\n"
                    f"   • Получение фото через QR-код прямо на мобильное устройство\n"
                    f"   • Полный брендинг фото зоны и программного обеспечения\n\n"
                    f"⏳ **Заказы:**\n"
                    f"   • Минимальное время — 3 часа\n"
                    f"   • Стоимость: 1 час — 100 тысяч тг\n\n"
                    f"💡 **Дополнительно:**\n"
                    f"Изготавливаем Фото-Будки и Селфи-Зеркала с ИИ под заказ\n\n"
                    f"☎ **Контакты:** +7 707 33 88 591 (Дияр)\n\n"
                    
                    f"• **Доп. информация:**\n"
                    f"   📸 Instagram: https://www.instagram.com/abai.event\n"
                    f"   ⏳ Минимальное время заказа: 3 часа (заказы менее 3 часов не принимаются)\n"
                    f"   💰 Стоимость: 3 часа — 300 тысяч тенге\n"
                    f"   🚫 Фотобудки не продаются, только сдаются в аренду\n\n"
                    
                    f"Если пользователь хочет узнать больше, задай вопрос:\n"
                    f"❓ Какую информацию вы бы хотели узнать и чем я могу вам помочь?\n\n"
                    
                    f"📋 **Варианты запроса:**\n"
                    f"   1️⃣ Стили обработки ИИ\n"
                    f"   2️⃣ Примеры фотографий до/после\n"
                    f"   3️⃣ Информация о деятельности нашей компании\n"
                    f"   4️⃣ Преимущества нашей компании\n"
                    f"   5️⃣ Что такое зона с нейросетью?\n"
                    f"   6️⃣ Какие имеются фотобудки и селфи зеркала?\n"
                    f"   7️⃣ Забронировать время на мероприятие\n"
                    f"   8️⃣ Посмотреть презентации о компании\n"
                    f"   9️⃣ Посмотреть видео о компании\n\n"
                    
                    f"💬 **Ответы:**\n"
                    f"1️⃣ **Стили обработки ИИ**\n"
                    f"   • На русском: \"Стиль обработки фото вы можете выбрать самостоятельно из списка доступных тем или придумать свой индивидуальный стиль, который наша нейросеть подготовит и реализует специально для вас.\"\n"
                    f"   • На казахском: \"Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз.\"\n"
                    f"   • На английском: \"You can choose the photo processing style yourself from the available themes or create your own individual style, which our neural network will prepare and implement especially for you.\"\n\n"
                    
                    f"2️⃣ **Примеры фотографий до/после**\n"
                    f"   • На русском: \"Сейчас отправлю примеры фото с наложенным ИИ, либо вы можете подробнее ознакомиться с ними в нашем Instagram: https://www.instagram.com/abai.event\"\n"
                    f"   • На казахском: \"Енді мен AI салынған фотосуреттердің мысалдарын жіберемін, немесе сіз оларды толығырақ біздің Instagram-да оқи аласыз: https://www.instagram.com/abai.event\"\n"
                    f"   • На английском: \"Now I will send examples of photos with superimposed AI, or you can view them in more detail on our Instagram: https://www.instagram.com/abai.event\"\n\n"
                    
                    f"3️⃣ **Информация о деятельности компании**\n"
                    f"   • На русском: \"Наша компания предлагает инновационные фотобудки с обработкой фото с помощью ИИ. Мы зарекомендовали себя среди крупных компаний, предоставляя качественные и удобные решения для мероприятий. Нам доверяют:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Казахстанская федерация футбола\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • Белый Медведь\n"
                    f"         • И многие другие.\"\n"
                    f"   • На казахском: \"Біздің компания AI көмегімен фото өңдеуі бар инновациялық фотостендтерді ұсынады. Біз жоғары сапалы және ыңғайлы іс-шаралар шешімдерін ұсынып, ірі компаниялар арасында өзімізді таныттық. Бізге сенетіндер:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Қазақстан футбол федерациясы\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • Ақ аю\n"
                    f"         • Және басқалар.\"\n"
                    f"   • На английском: \"Our company offers innovative photo booths with AI photo processing. We have established ourselves among major companies by providing high-quality and convenient event solutions. Trusted by:\n"
                    f"         • Air Astana\n"
                    f"         • KASPI\n"
                    f"         • Almaty Marathon\n"
                    f"         • Kazakhstan Football Federation\n"
                    f"         • ALTEL/TELE2\n"
                    f"         • ACTIV\n"
                    f"         • White Bear\n"
                    f"         • And many others.\"\n\n"
                    
                    f"4️⃣ **Преимущества нашей компании**\n"
                    f"   • На русском: \"Индивидуальный подход к мероприятию — более 100 стилей обработки фото, включая ИИ. Моментальная обработка, печать, отправка или получение через QR-код. Фото зоны 'Под ключ' с полным техническим сопровождением (транспортировка, администрирование).\"\n"
                    f"   • На казахском: \"Іс-шараға жеке көзқарас — фотосуреттерді өңдеудің 100-ден астам стилі, оның ішінде Neural Network арқылы. Жылдам фото өңдеу, басып шығару немесе QR арқылы алу. 'Кілтке' фото аймақтары толық техникалық қолдаумен қамтамасыз етіледі.\"\n"
                    f"   • На английском: \"Individual approach to events — over 100 photo processing styles including AI. Instant processing, printing, sending, or receiving via QR. 'Pod klyuch' photo zones with full technical support (transportation, administration).\"\n\n"
                    
                    f"5️⃣ **Что такое зона с нейросетью?**\n"
                    f"   • На русском: \"Фото зона состоит из фото-будки или селфи-зеркала и принтера, которые можно установить в удобном месте на вашем мероприятии. Гости смогут получить моментальное фото, обработанное ИИ под вашу тематику, или выбрать индивидуальный дизайн обработки. Детали обсуждаются с нашим администратором.\"\n"
                    f"   • На казахском: \"Фотоаймақ фотобудка немесе селфи айнасы мен принтерден тұрады, оны іс-шараңызда ыңғайлы жерде орнатуға болады. Қонақтарыңыз лезде AI өңдеген фото ала алады немесе жеке дизайн таңдай алады. Толығырақ біздің әкімшімен талқыланады.\"\n"
                    f"   • На английском: \"The photo zone consists of a photo booth or selfie mirror and a printer, which can be set up in a convenient location at your event. Guests can instantly receive photos processed by AI according to your theme, or choose an individual design. Details will be discussed with our administrator.\"\n\n"
                    
                    f"6️⃣ **Какие имеются фотобудки и селфи зеркала?**\n"
                    f"   • На русском: \"На данный момент имеются 2 фотобудки и 2 селфи зеркала.\"\n"
                    f"   • На казахском: \"Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар.\"\n"
                    f"   • На английском: \"At the moment, there are 2 photo booths and 2 selfie mirrors.\"\n\n"
                    
                    f"7️⃣ **Забронировать время на мероприятие**\n"
                    f"   • На русском: \"Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону: +7 707 33 88 591 (WhatsApp, Telegram) или через Instagram: https://www.instagram.com/abai.event\"\n"
                    f"   • На казахском: \"Фотоаймақ немесе Selfie Mirror қызметін +7 707 33 88 591 (WhatsApp, Telegram) телефоны арқылы немесе Instagram: https://www.instagram.com/abai.event арқылы брондауға болады.\"\n"
                    f"   • На английском: \"You can book the Photo Zone or Selfie Mirror service by phone: +7 707 33 88 591 (WhatsApp, Telegram) or via Instagram: https://www.instagram.com/abai.event\"\n\n"
                    
                    f"8️⃣ **Посмотреть презентации о компании**\n"
                    f"   • На русском: \"Сейчас скину информативные презентации о компании.\"\n"
                    f"   • На казахском: \"Қазір компания туралы ақпараттық презентацияларды жіберемін.\"\n"
                    f"   • На английском: \"I will now send you the informative presentations about the company.\"\n\n"
                    
                    f"9️⃣ **Посмотреть видео о компании**\n"
                    f"   • На русском: \"Сейчас скину видео о компании.\"\n"
                    f"   • На казахском: \"Қазір компания туралы бейнені жіберемін.\"\n"
                    f"   • На английском: \"I'll send you a video about the company now.\"\n\n"
                    
                    f"🔹 **Специальные запросы:**\n"
                    f"   1️⃣ Стиль обработки фото (вариант 1).\n"
                    f"   2️⃣ Примеры фото до/после (вариант 2).\n"
                    f"   6️⃣ Фотобудки и селфи зеркала (вариант 6).\n"
                    f"   7️⃣ Контакты для бронирования (вариант 7):\n"
                    f"      'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграм https://www.instagram.com/abai.event'\n"
                    f"   8️⃣ Презентации о компании (вариант 8).\n"
                    f"   9️⃣ Видео о компании (вариант 9).\n\n"
                    
                    f"При смене языка отправляй соответствующий текст. Если с тобой пишут на другом языке — уточняй смену языка."
                )
                sgen_text = get_mess(message.text, prompt, True, dialog)

            print("-" * 80)
            print(dates_text)
            dialog.append({"role": "user", "message": message.text})
            dialog.append({"role": "assistant", "message": sgen_text})
            save_dialog_to_db(message.chat.id, dialog)
            print("-" * 80)
            print(dialog)
            bot.send_message(message.chat.id, sgen_text)

            # Обработка специальных запросов и смены языка
            process_special_requests(sgen_text, message)

    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)


def process_special_requests(sgen_text, message):
    # 🔄 Обработка смены языка
    if "Switching language to English." in sgen_text:
        add_language(message.chat.id, "English")
    elif "Смена языка на русский." in sgen_text:
        add_language(message.chat.id, "Russian")
    elif "Тілді қазақ тіліне ауыстыру." in sgen_text:
        add_language(message.chat.id, "Kazakh")

    # 📸 Вариант 1: Стиль обработки фото
    if any(sub in sgen_text for sub in [
        "Стиль обработки фото вы можете выбрать самостоятельно из списка доступных тем или придумать свой индивидуальный стиль, который наша нейросеть подготовит и реализует специально для вас",
        "You can choose the photo processing style yourself from the available themes or create your own individual style, which our neural network will prepare and implement especially for you",
        "Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз"
    ]):
        folders = get_folders('styles')
        if folders:
            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        with open(image_path, 'rb') as img_file:
                            bot.send_photo(message.chat.id, img_file)
                    folder_name = os.path.basename(folder)
                    bot.send_message(message.chat.id, folder_name)

    # 🖼️ Вариант 2: Примеры фото до/после
    elif any(sub in sgen_text for sub in [
        "Сейчас отправлю примеры фото с наложенным ИИ",
        "Now I will send examples of photos with superimposed AI",
        "Енді мен AI салынған фотосуреттердің мысалдарын жіберемін"
    ]):
        images = get_files('examples')
        if images:
            for image_path in images:
                with open(image_path, 'rb') as img_file:
                    bot.send_photo(message.chat.id, img_file)

    # 📷 Вариант 6: Фотобудки и селфи зеркала
    elif any(sub in sgen_text for sub in [
        "На данный момент имеются 2 фотобудки и 2 селфи зеркала",
        "Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:",
        "At the moment there are 2 photo booths and 2 selfie mirrors:"
    ]):
        folders = get_folders('photobooth')
        language_map = {"Русский": "ru", "English": "en", "Kazakh": "kk"}
        user_language = get_language_by_user_id(message.chat.id)
        target_language = language_map.get(user_language, "ru")
        if folders:
            for folder in folders:
                images = get_files(folder)
                if images:
                    for image_path in images:
                        with open(image_path, 'rb') as img_file:
                            bot.send_photo(message.chat.id, img_file)
                    folder_name = os.path.basename(folder)
                    translated_folder_name = translate_folder_name(folder_name, target_language)
                    bot.send_message(message.chat.id, translated_folder_name)

    # 📊 Вариант 8: Презентации о компании
    elif any(sub in sgen_text for sub in [
        "Сейчас скину информирующие презентации о компании",
        "I will now send you the informative presentations about the company",
        "Қазір компания туралы ақпараттық презентацияларды жіберемін"
    ]):
        presentations = get_files("presentations")
        if presentations:
            for presentation in presentations:
                with open(presentation, 'rb') as presentation_file:
                    bot.send_document(message.chat.id, presentation_file)

    # 🎥 Вариант 9: Видео о компании
    elif any(sub in sgen_text for sub in [
        "Сейчас скину видео о компании",
        "I'll send you a video about the company now",
        "Қазір компания туралы бейнені жіберемін"
    ]):
        videos = get_files("videos")
        if videos:
            for video in videos:
                with open(video, 'rb') as video_file:
                    bot.send_document(message.chat.id, video_file)


# *--------------------------------------------------------------------------------------------!
# *----------------------------------- ЗАПУСК -------------------------------------------------!
# *--------------------------------------------------------------------------------------------!

if __name__ == "__main__":
    bot.infinity_polling()
