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
        if not message.text or not isinstance(message.text, str):  # Проверка текста сообщения
            bot.send_message(message.chat.id, "Ошибка: Пустое сообщение. Введите текст.")
            return
        if not message.text.startswith('!'):
            dialog1 = get_dialog_from_db(message.chat.id)
            if len(dialog1) >= 20:
                del dialog1[:len(dialog1) - 20]
            all_dates = get_all_dates_from_db()
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            print(get_language_by_user_id(message.chat.id))
            #encoded_query = urllib.parse.quote(message.text)
            company_text, company_info, question_text = open_txt_files()
            if get_language_by_user_id(message.chat.id) == "NONE":
                print("Нету языка")
                sgen_text = get_mess(message.text, f"""Ты искуственный помощник технической поддержки компании 'AbAi event', но у пользователя на данный момент не установлен язык, твоя цель сейчас спросить про язык, на котором пользователю будет удобно общаться, вот вопрос который ты должен задавать:
                                                          'Выберите язык для удобного взаимодействия \n -Қазақша 🇰🇿 \n -Русский 🇷🇺 \n -English 🇬🇧 \n'
                                                          Если пользователь ответил, что хочет сменить язык например на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Все запросы и команды ты обрабатываешь на языке пользователя. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь
                                                          От темы не уходи, на вопросы, помимо темы с языками, ты не отвечаешь, ты переспрашиваешь у пользователя на который язык он хочет установить, спрашиваешь ты это, сразу на трёх языках, предлагая доступные варианты, твоя цель установить на каком языке хочет общаться пользователь и в зависимости от этого сменить его язык фразой 'Смена языка на 'название языка''""", True, dialog1)
            else:
                sgen_text = get_mess(message.text, f"""Ты искусственный помощник технической поддержки компании 'AbAi event', отвечающий на языке, смотря на каком с тобой общаются, только на вопроса по поводу компании, брони либо связанные как то с компанией, так же ты добавляешь для дизайна эмодзи ко всему тексту, который отправляешь, если есть перечисление, то по теме перечисления на каждую строчку добавляешь эмодзи
                                                          ты отвечаешь на вопросы по поводу компании и по поводу брони, так же ты просто разговариваешь с пользователем если он ведёт с тобой диалог, если человек спрашивает про бронь, ты отвечаешь занят день или нет, если занят, то какими будками, список занятых дат,
                                                          а также колонок: {check_dates_and_cabins()}, если в списке нету даты, значит нету брони, а также пиши пользователю свободные кабинки в виде списка если дата свободна. Сегодняшние дата и время - {getDateAndTime()} 
                                                          Информационный текст в котором расписаны случаи, как на что отвечать и различная информация: {company_text}
                                                          Различная информация про компанию и не только, имея данную информацию, ты отвечаешь на вопросы, смотря на каком языке с тобой общается пользователь: {company_info}
                                                          Если пользователь хочет забронировать день (оно находится под цифрой 7, после уточняющего вопроса), то ты должен скинуть ему следующие контактные данные: 'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграмм https://www.instagram.com/abai.event'
                                                          Если пользователь хочет узнать информацию о компании, то ты ему рассказываешь про компанию, так же спрашиваешь хочет ли пользователь получить больше информации про компанию, если он скажет, что хочет, то ты должен будешь спросить у него на языке пользователя информацию из данного текста: '{question_text}'
                                                          Если пользователь говорит, что хочет узнать про стили обработки ИИ(оно находится под цифрой 1, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас.'
                                                          Если пользователь говорит, что хочет узнать про примеры фотографий до/после(оно находится под цифрой 2, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас отправлю примеры фото с наложенным ИИ, либо же вы можете более подробно ознакомиться с ними в нашем Инстаграме https://www.instagram.com/abai.event', ссылку отправляешь только один раз и без лишних спец знаков, просто ссылку
                                                          Если пользователь говорит, что хочет узнать про фотобудки и селфи зеркала(оно находится под цифрой 6, после уточняющего вопроса), либо если пользователь просит скинуть фотографии фотобудок, то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала:' если русский, 'Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:' если казахский, 'At the moment there are 2 photo booths and 2 selfie mirrors:' если английский
                                                          Если пользователь говорит, что хочет посмотреть презентации о компании(оно находится под цифрой 8, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас скину информирующие презентации о компании'
                                                          Если пользователь говорит, что хочет посмотреть видео о компании(оно находится под цифрой 9, после уточняющего вопроса), то ты отправляешь именно этот текст на языке пользователя, никак не меняя его: 'Сейчас скину видео о компании'
                                                          Если пользователь хочет сменить язык на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Язык пользователя: {get_language_by_user_id(message.chat.id)}. Все запросы и команды ты обрабатываешь на языке пользователя и даже ответы на условия, в которых мы говорили отправлять только определённый текст, ты его переводишь и отправляешь на том языке, на котором с тобой пользователь говорил. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь
                                                          Если с тобой начинают говорить на другом языке отличного от установленного, поинтересуйся о смене языка пользователя
                                                          Если пользователь просит тебя показать фотобудки и зеркала, либо спрашивает как они выглядят, то ты добавляешь этот текст на языке пользователя к предыдущему тексту, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала'
                                                          Также могут быть дополнительные вопросы: {format_QA_table}
                                                          И может быть допоолнительная информация: {format_info_table}
                                                          """
                                                          ,True, dialog1)
            print("-" * 80)
            print(dates_text)
            dialog1.append({"role": "user", "content": [{ "type": "text", "text": f"{message.text}" }]})
            dialog1.append({"role": "assistant", "content": [{ "type": "text", "text": f"{sgen_text}" }]})
            save_dialog_to_db(message.chat.id, dialog1)
            print("-" * 80)
            print(dialog1)
            bot.send_message(message.chat.id, sgen_text)
            if "Switching language to English." in sgen_text:
                add_language(message.chat.id, "English")
            if "Смена языка на русский." in sgen_text:
                add_language(message.chat.id, "Russian")
            if "Тілді қазақ тіліне ауыстыру." in sgen_text:
                add_language(message.chat.id, "Kazakh")
            elif "Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас" in sgen_text or "You can choose the photo processing style yourself from the list of available themes, or come up with your own individual style, which our neural network will prepare and implement especially for you" in sgen_text or "Сіз бұрыннан бар тақырыптар тізімінен фотосуреттерді өңдеу стилін өзіңіз таңдай аласыз немесе біздің нейрондық желі арнайы сіз үшін дайындап, жүзеге асыратын өзіңіздің жеке стильіңізді таба аласыз" in sgen_text:
                folders = get_folders('styles')
                if folders:
                    for folder in folders:
                        images = get_files(folder)
                        if images:
                            # Отправляем все изображения
                            for image_path in images:
                                with open(image_path, 'rb') as img_file:
                                    bot.send_photo(message.chat.id, img_file)
                            # После отправки всех изображений отправляем название папки
                            folder_name = os.path.basename(folder)
                            bot.send_message(message.chat.id, folder_name)
            elif "Сейчас отправлю примеры фото с наложенным ИИ" in sgen_text or "Now I will send examples of photos with superimposed AI" in sgen_text or "Енді мен AI салынған фотосуреттердің мысалдарын жіберемін" in sgen_text:
                images = get_files('examples')
                if images:
                    # Отправляем все изображения
                    for image_path in images:
                        with open(image_path, 'rb') as img_file:
                            bot.send_photo(message.chat.id, img_file)
            elif "На данный момент имеются 2 фотобудки и 2 селфи зеркала" in sgen_text or "Қазіргі уақытта 2 фотостенд және 2 селфи айнасы бар:" in sgen_text or "At the moment there are 2 photo booths and 2 selfie mirrors:" in sgen_text:
                folders = get_folders('photobooth')
                language_map = {
                    "Русский": "ru",
                    "English": "en",
                    "Kazakh": "kk"
                }

                if folders:
                    user_language = get_language_by_user_id(message.chat.id)
                    target_language = language_map.get(user_language, "ru")
                    for folder in folders:
                        images = get_files(folder)
                        if images:
                            for image_path in images:
                                with open(image_path, 'rb') as img_file:
                                    bot.send_photo(message.chat.id, img_file)
                            # После отправки всех изображений отправляем название папки
                            folder_name = os.path.basename(folder)
                            translated_folder_name = translate_folder_name(folder_name, target_language)
                            bot.send_message(message.chat.id, translated_folder_name)
            elif "Сейчас скину информирующие презентации о компании" in sgen_text or "I will now send you the informative presentations about the company" in sgen_text or "Қазір компания туралы ақпараттық презентацияларды жіберемін" in sgen_text:
                presentations = get_files("presentations")
                if presentations:
                    for presentation in presentations:
                        with open(presentation, 'rb') as presentation_file:
                            bot.send_document(message.chat.id, presentation_file)
            elif "Сейчас скину видео о компании" in sgen_text or "I'll send you a video about the company now" in sgen_text or "Қазір компания туралы бейнені жіберемін" in sgen_text:
                videos = get_files("videos")
                if videos:
                    for video in videos:
                        with open(video, 'rb') as video_file:
                            bot.send_document(message.chat.id, video_file)
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
