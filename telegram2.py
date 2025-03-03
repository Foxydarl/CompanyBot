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
    "!вопросы-ответы\n"
    "!удалить-вопрос-ответ\n"
    "!добавить-вопрос-ответ\n"
    "!информация\n"
    "!удалить-информацию\n"
    "!добавить-информацию\n"
    "!пользователи\n"
    "!админы\n"
    "!удалить-админа\n"
    "!добавить-админа\n"
    "!добавить-колонку <название_продолжение>\n"
    "!удалить-колонку <название_продолжение>\n"
    "!обновить-слот <дата> <колонка> <статус>\n"
    "!показать-таблицу\n"
    "!забронировать <дата> <колонка>\n"
    "!добавить-данные-о-кабинках\n"
    "!ожидающие-ответа\n"
    "!добавить-дату\n"
    "!удалить-дату\n"
    "!добавить-файл\n"
    "!остановить-чат\n"
    "!остановить-чат"
)

@bot.message_handler(func=lambda message: message.text.startswith('!пользователи') and message.from_user.username in check_admins()[1])
def handle_show_users(message):
    formatted_table = format_users_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

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

@bot.message_handler(func=lambda message: message.text.startswith('!команды') and message.from_user.username in check_admins()[1])
def handle_show_commands(message):
    bot.send_message(message.chat.id, info_about_commands)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-колонку') and message.from_user.username in check_admins()[1])
def handle_add_column_cmd(message):
    try:
        column_name = message.text.split(" ", 1)[1]
        result = add_column(column_name)
    except IndexError:
        result = "⚠️ Используйте: !добавить-колонку <название_продолжение>"
    bot.reply_to(message, result)

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

# ------------------------------------
# Ниже - ваш основной message_handler, который генерирует ответы
# ------------------------------------
@bot.message_handler(content_types=["text"])
def welcome(message):
    add_user(message)
    try:
        if not message.text.startswith('!'):
            # Получаем диалог из БД
            dialog1 = get_dialog_from_db(message.chat.id)
            if len(dialog1) >= 20:
                del dialog1[:len(dialog1) - 20]

            all_dates = get_all_dates_from_db()
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."

            # Загружаем тексты из БД, а не из txt
            company_text, company_info, question_text = open_txt_files()

            # Если у пользователя не установлен язык
            if get_language_by_user_id(message.chat.id) == "NONE":
                sgen_text = get_mess(
                    message.text,
                    ("Ты искуственный помощник ... [сюда подставляете большой промпт] \n"
                     "Спроси про язык, на котором удобно ..."),
                    True,
                    dialog1
                )
            else:
                # Формируем ваш промпт, используя company_text, company_info, question_text
                sgen_text = get_mess(
                    message.text,
                    f"Ты искусственный помощник ...\n"
                    f"Информационный текст: {company_text}\n"
                    f"Различная информация: {company_info}\n"
                    f"Список вопросов: {question_text}\n"
                    f"Сегодняшняя дата и время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
                    f"Свободные/занятые даты: {check_dates_and_cabins()}\n"
                    f"Язык пользователя: {get_language_by_user_id(message.chat.id)}\n",
                    True,
                    dialog1
                )

            dialog1.append({"role": "user", "message": message.text})
            dialog1.append({"role": "assistant", "message": sgen_text})
            save_dialog_to_db(message.chat.id, dialog1)
            bot.send_message(message.chat.id, sgen_text)

            # Проверяем, вдруг была смена языка
            if "Switching language to English." in sgen_text:
                add_language(message.chat.id, "English")
            if "Смена языка на русский." in sgen_text:
                add_language(message.chat.id, "Russian")
            if "Тілді қазақ тіліне ауыстыру." in sgen_text:
                add_language(message.chat.id, "Kazakh")

            # Если есть какие-то особые проверки ("Если в тексте упоминается X, то отправить файл/картинку"), делайте их здесь:
            # Пример с фотобудками, презентациями и т.д.
            if ("На данный момент имеются 2 фотобудки" in sgen_text) or ("Қазіргі уақытта 2 фотостенд" in sgen_text) or ("At the moment there are 2 photo booths" in sgen_text):
                folders = [os.path.join("photobooth", x) for x in os.listdir("photobooth") if os.path.isdir(os.path.join("photobooth", x))]
                language_map = {
                    "Russian": "ru",
                    "English": "en",
                    "Kazakh": "kk"
                }
                user_language = get_language_by_user_id(message.chat.id)
                target_language = language_map.get(user_language, "ru")
                for folder in folders:
                    images = get_files(folder)
                    for image_path in images:
                        with open(image_path, 'rb') as img_file:
                            bot.send_photo(message.chat.id, img_file)
                    folder_name = os.path.basename(folder)
                    translated_folder_name = translate_folder_name(folder_name, target_language)
                    bot.send_message(message.chat.id, translated_folder_name)

            elif ("Сейчас скину информирующие презентации" in sgen_text) or ("I will now send you the informative presentations" in sgen_text) or ("компания туралы ақпараттық презентацияларды" in sgen_text):
                presentations = get_files("presentations")
                for presentation in presentations:
                    with open(presentation, 'rb') as presentation_file:
                        bot.send_document(message.chat.id, presentation_file)

            elif ("Сейчас скину видео о компании" in sgen_text) or ("I'll send you a video about the company now" in sgen_text) or ("компания туралы бейнені жіберемін" in sgen_text):
                videos = get_files("videos")
                for video in videos:
                    with open(video, 'rb') as video_file:
                        bot.send_document(message.chat.id, video_file)

            elif ("Сейчас отправлю примеры фото с наложенным ИИ" in sgen_text) or ("Now I will send examples of photos with superimposed AI" in sgen_text) or ("Енді мен AI салынған фотосуреттердің мысалдарын" in sgen_text):
                images = get_files("examples")
                for image_path in images:
                    with open(image_path, 'rb') as img_file:
                        bot.send_photo(message.chat.id, img_file)

            elif ("Стиль обработки фото вы можете выбрать самостоятельно" in sgen_text) or ("You can choose the photo processing style" in sgen_text) or ("Сіз бұрыннан бар тақырыптар тізімінен" in sgen_text):
                folders = [os.path.join("styles", x) for x in os.listdir("styles") if os.path.isdir(os.path.join("styles", x))]
                for folder in folders:
                    images = get_files(folder)
                    for image_path in images:
                        with open(image_path, 'rb') as img_file:
                            bot.send_photo(message.chat.id, img_file)
                    folder_name = os.path.basename(folder)
                    bot.send_message(message.chat.id, folder_name)

    except TypeError as e:
        error_text = e.args[0]
        print(error_text)

if __name__ == "__main__":
    bot.infinity_polling()
