# -*- coding: utf-8 -*-
import telebot
from methods import *
from HelperDB import *
import urllib.parse

create_folders()
createDataBase()

a = int(input())
if a == 1 : bot = telebot.TeleBot("7947945450:AAHOqe3od-WjvsnHeBb_TcQol7iVLFcahJA")
else: bot = telebot.TeleBot("6514999735:AAHO4Ypc87aYUZ8nbDTMp6Ny8ULepl6c3fE")
#bot = telebot.TeleBot("7947945450:AAHOqe3od-WjvsnHeBb_TcQol7iVLFcahJA")
dialog = []
info_about_commands = ("Информация о командах:\n!показать-вопросы\n!удалить-вопрос-ответ ?вопрос\n!добавить-вопрос-ответ ?вопрос !ответ\n!пользователи\n!админы\n!удалить-админа\n!добавить-админа\n!добавить-колонку <название_продолжение>\n!удалить-колонку <название_продолжение>\n!обновить-слот <дата> <колонка> <статус>"
                       "\n!показать-таблицу\n!забронировать <дата> <колонка>\n!добавить-данные-о-кабинках\n!ожидающие-ответа\n!добавить-дату\n!удалить-дату"
                       "\n!добавить-файл\n!остановить-чат\n!остановить-чат")

@bot.message_handler(func=lambda message: message.text.startswith('!пользователи') and message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    formatted_table = format_users_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!админы') and message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    formatted_table = format_admins_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!завершить-чат') and not message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    change_waiting_flag_false(message.chat.id)
    bot.send_message(message.chat.id, "Чат с админом завершен.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-админа') and message.from_user.username in check_admins()[1])
def handle_add_column(message):
    try:
        username = message.text.split(" ", 1)[1]
        result = delete_admin(username)
    except Exception:
        result = "⚠️ Не получилось удалить админа."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-админа') and message.from_user.username in check_admins()[1])
def handle_add_column(message):
    try:
        username = message.text.split(" ", 1)[1]
        result = add_admin(username)
    except Exception as e:
        print(f"Error: {e}")
        result = "⚠️ Не получилось добавить админа."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!команды') and message.from_user.username in check_admins()[1])
def handle_add_column(message):
    bot.send_message(message.chat.id, info_about_commands)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-колонку') and message.from_user.username in check_admins()[1])
def handle_add_column(message):
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
def handle_remove_column(message):
    try:
        column_name = message.text.split(" ", 1)[1]
        result = remove_column(column_name)
    except IndexError:
        result = "⚠️ Используйте: !удалить-колонку <название_продолжение>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!обновить-бронь-даты') and message.from_user.username in check_admins()[1])
def handle_update_slot(message):
    try:
        if message.text == "выйти":
            bot.send_message(message.chat.id, "Выхожу из функции.")
            return
        _, date, column_name, status = message.text.split(" ", 3)
        if status != "free" or "booked":
            bot.send_message(message.chat.id, "В качестве статуса используйте <free> или <booked>")
            bot.register_next_step_handler(message, handle_update_slot)
        result = update_slot(date, column_name, status)
    except ValueError:
        result = "⚠️ Используйте: !обновить-бронь-даты <дата> <колонка> <статус>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!показать-таблицу') and message.from_user.username in check_admins()[1])
def handle_view_dates(message):
    formatted_table = format_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!забронировать') and message.from_user.username in check_admins()[1])
def handle_book_slot(message):
    try:
        _, date, column_name = message.text.split(" ", 2)
        result = book_slot(date, column_name)
    except ValueError:
        result = "⚠️ Используйте: !забронировать <дата> <колонка>"
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-данные-о-кабинках') and message.from_user.username in check_admins()[1])
def handle_add_cabins(message):
    if message.from_user.username in check_admins()[1]:
        bot.send_message(message.chat.id, "Введите информацию о кабинках")
        bot.register_next_step_handler(message, add_cabin)
def add_cabin(message):
    write_file("cabins", message.text)

@bot.message_handler(func=lambda message: message.text.startswith('!ожидающие-ответа') and message.from_user.username in check_admins()[1])
def show_waiting_users(message):
    waiting_users = get_waiting_users()
    if waiting_users:
        waiting_list = "\n".join(map(str, waiting_users))
        bot.send_message(message.chat.id, f"Список ожидающих пользователей:\n{waiting_list}")
    else:
        bot.send_message(message.chat.id, "Нет пользователей, ожидающих ответа.")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-дату') and message.from_user.username in check_admins()[1])
def handle_add_date(message):
    data = message.text[len('!добавить-дату '):].strip()
    if data:
        result = save_data_to_db(data)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Не была указана дата. Пожалуйста, введите её.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-дату') and message.from_user.username in check_admins()[1])
def handle_delete_date(message):
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
            # Проверяем содержимое папки
            contents = os.listdir(target_folder_path)
            if contents:
                bot.send_message(message.chat.id, f"В папке '{folder_name}' есть файлы или подпапки. Вы уверены, что хотите удалить её? (да/нет)")
                bot.register_next_step_handler(message, delete_folder_with_confirmation, target_folder_path)
            else:
                # Папка пуста, можно удалить сразу
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
                    delete_folder_contents(item_path)  # Рекурсивно удаляем подпапки
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
    bot.register_next_step_handler(message, process_file, os.getcwd())  # Передаем текущую директорию
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

        if not check[1] and not check[2]:  # Папка пуста
            bot.send_message(message.chat.id, "Можете отправить файл, и я добавлю его в данную папку.")
            bot.register_next_step_handler(message, save_file, target_path)

        elif check[1] and check[2] is None:  # Есть подпапки, но нет файлов
            bot.register_next_step_handler(message, process_file, target_path)

        elif not check[1] and check[2]:  # Есть только файлы
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
            # Определяем тип файла
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                original_name = message.document.file_name
            elif message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)  # Берем фото с наибольшим разрешением
                original_name = "photo.jpg"  # Указываем стандартное имя
            elif message.video:
                file_info = bot.get_file(message.video.file_id)
                original_name = "video.mp4"  # Указываем стандартное имя

            # Скачиваем файл
            downloaded_file = bot.download_file(file_info.file_path)

            # Запрос названия файла у пользователя
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

        # Определяем расширение файла
        file_extension = os.path.splitext(original_name)[1]
        final_name = f"{custom_name}{file_extension}"

        # Сохраняем файл
        file_path = os.path.join(folder_path, final_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(file_data)

        bot.send_message(message.chat.id, f"Файл '{final_name}' успешно сохранен в папке '{folder_path}'.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении файла с названием: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!остановить-чат') and message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    bot.send_message(message.chat.id, "Введите chatId с которым хотите завершить чат.")
    bot.register_next_step_handler(message, process_stop_chat)
def process_stop_chat(message):
    change_waiting_flag_false(message.text)
    bot.send_message(message.chat.id, f"Чат с {message.text} завершен.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл'))
def handle_delete_file(message):
    bot.send_message(message.chat.id, f"Укажите папку, в которой вы хотите удалить файл.\n{display_files()}")
    bot.register_next_step_handler(message, process_delete_file, os.getcwd())  # Передаем текущую директорию
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

        if not check[1] and not check[2]:  # Папка пуста
            bot.send_message(message.chat.id, "В данной папке нет файлов для удаления.")
            return

        elif not check[1] and check[2]:  # Есть только файлы
            bot.send_message(message.chat.id, "Укажите название файла, который вы хотите удалить, или напишите <Выйти>.")
            bot.register_next_step_handler(message, delete_file, target_path)

        elif check[1] and check[2] is None:  # Есть подпапки, но нет файлов
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

@bot.message_handler(func=lambda message: message.from_user.username in check_admins()[1] and "Сообщение" in message.text)
def handle_admin_reply(message):
    try:
        if "Сообщение:" in message.text:
            parts = message.text.split("Сообщение:")
            user_id = parts[0].strip()
            reply_text = parts[1].strip()
            if user_id.isdigit():
                user_id = int(user_id)
                bot.send_message(user_id, f"Сообщение от администратора: {reply_text}")
                bot.send_message(message.chat.id, f"Сообщение успешно отправлено пользователю {user_id}.")
            else:
                bot.send_message(message.chat.id, "Некорректный формат ID пользователя. Убедитесь, что это число.")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, используйте формат: <user_id> Сообщение: <текст ответа>")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(f"Error in handle_admin_reply: {e}")


@bot.message_handler(content_types=["text"])
def welcome(message):
    add_user(message)
    try:
        print(message)
        if not message.text.startswith('!'):
            if not check_waiting_status(message.chat.id):
                dialog1 = get_dialog_from_db(message.chat.id)
                if len(dialog1) >= 20:
                    del dialog1[:len(dialog1) - 20]
                all_dates = get_all_dates_from_db()
                dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
                print(get_language_by_user_id(message.chat.id))
                encoded_query = urllib.parse.quote(message.text)
                company_text, company_info, question_text = open_txt_files()
                if get_language_by_user_id(message.chat.id) == "NONE":
                    print("Нету языка")
                    sgen_text = get_mess(message.text, "Ты искуственный помощник технической поддержки компании 'AbAi event', но у пользователя на данный момент не установлен язык, твоя цель сейчас спросить про язык, на котором пользователю будет удобно общаться, вот вопрос который ты должен задавать:"
                                                              "'Выберите язык для удобного взаимодействия \n -Қазақша 🇰🇿 \n -Русский 🇷🇺 \n -English 🇬🇧 \n'"
                                                              f"Если пользователь ответил, что хочет сменить язык например на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Все запросы и команды ты обрабатываешь на языке пользователя. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь"
                                                              f"От темы не уходи, на вопросы, помимо темы с языками, ты не отвечаешь, ты переспрашиваешь у пользователя на который язык он хочет установить, спрашиваешь ты это, сразу на трёх языках, предлагая доступные варианты, твоя цель установить на каком языке хочет общаться пользователь и в зависимости от этого сменить его язык фразой 'Смена языка на 'название языка''", True, dialog1)
                else:
                    sgen_text = get_mess(message.text, f"Ты искусственный помощник технической поддержки компании 'AbAi event', отвечающий на языке, смотря на каком с тобой общаются, только на вопроса по поводу компании, брони либо связанные как то с компанией, так же ты добавляешь для дизайна эмодзи ко всему тексту, который отправляешь"
                                                              f"ты отвечаешь на вопросы по поводу компании и по поводу брони, так же ты просто разговариваешь с пользователем если он ведёт с тобой диалог, если человек спрашивает про бронь, ты отвечаешь занят день или нет, если занят, то какими будками, список занятых дат,"
                                                              f"а также колонок: {check_dates_and_cabins()}, если в списке нету даты, значит нету брони, а также пиши пользователю свободные кабинки в виде списка если дата свободна. Сегодняшние дата и время - {getDateAndTime(message)} "
                                                              f"Информационный текст в котором расписаны случаи, как на что отвечать и различная информация: {company_text}"
                                                              f"Различная информация про компанию и не только, имея данную информацию, ты отвечаешь на вопросы, смотря на каком языке с тобой общается пользователь: {company_info}"
                                                              f"Если пользователь хочет забронировать день (оно находится под цифрой 7, после уточняющего вопроса), то ты должен скинуть ему контактные данные менеджера продаж, затем спросить у пользователя данный текст: 'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграмм https://www.instagram.com/abai.event', после положительного ответа отправляй ему именно этот текст никак не меняя его:Я вас направляю к менеджеру продаж, все подробности, а также бронирование можете обсудить с ним,если хотите завершить чат с админом введите !завершить-чат', так же скидываешь текст в котором будут ситуативные вопросы и вот там будет ответНо твоя основная роль информировать пользователя о наличии свободных дней."
                                                              f"Если пользователь хочет узнать информацию о компании, то ты ему рассказываешь про компанию, так же спрашиваешь хочет ли пользователь получить больше информации про компанию, если он скажет, что хочет, то ты будешь спросить у него информацию из данного текста: '{question_text}'"
                                                              f"Если пользователь говорит, что хочет узнать про стили обработки ИИ(оно находится под цифрой 1, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас.'"
                                                              f"Если пользователь говорит, что хочет узнать про примеры фотографий до/после(оно находится под цифрой 2, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас отправлю примеры фото с наложенным ИИ, либо же вы можете более подробно ознакомиться с ними в нашем Инстаграме https://www.instagram.com/abai.event', ссылку отправляешь только один раз и без лишних спец знаков, просто ссылку"
                                                              f"Если пользователь говорит, что хочет узнать про фотобудки и селфи зеркала(оно находится под цифрой 6, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала:'"
                                                              f"Если пользователь говорит, что хочет посмотреть презентации о компании(оно находится под цифрой 8, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас скину информирующие презентации о компании'"
                                                              f"Если пользователь говорит, что хочет посмотреть видео о компании(оно находится под цифрой 9, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас скину видео о компании'"
                                                              f"Если пользователь хочет сменить язык на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Данные о его языке: {get_language_by_user_id(message.chat.id)}. Все запросы и команды ты обрабатываешь на языке пользователя и ответы на условия ты отправляешь на языке пользователя. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь"
                                                              f"Если с тобой начинают говорить на другом языке отличного от установленного, поинтересуйся о смене языка пользователя"
                                                              f"Если пользователь интересуется о информации или задает не правильные вопросы не относящиеся к теме компании, или ты не получил информации которую хочет получит пользователь(но если ты можешь проанализировать информацию, то сначала проанализируй ее и дай верный ответ) отправляй ему только эту ссылку, без лишнего текста: 'https://google-poisk-vmesto-tebya.ru/?q={encoded_query}. Примечание: Если ты знаешь ответ, ссылку отправлять не надо."
                                                              ,True, dialog1)
                print("-" * 80)
                print(dates_text)
                dialog1.append({"role": "user", "message": message.text})
                dialog1.append({"role": "assistant", "message": sgen_text})
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
                if "Я вас направляю к менеджеру продаж, все подробности, а также бронирование можете обсудить с ним" in sgen_text:
                    notification_text = notify(message)
                    for admin_id in check_admins()[0]:
                        bot.send_message(admin_id, notification_text)
                elif "Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас." in sgen_text:
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
                elif "Сейчас отправлю примеры фото с наложенным ИИ" in sgen_text:
                    images = get_files('examples')
                    if images:
                        # Отправляем все изображения
                        for image_path in images:
                            with open(image_path, 'rb') as img_file:
                                bot.send_photo(message.chat.id, img_file)
                elif "На данный момент имеются 2 фотобудки и 2 селфи зеркала" in sgen_text:
                    folders = get_folders('photobooth')
                    if folders:
                        for folder in folders:
                            images = get_files(folder)
                            if images:
                                for image_path in images:
                                    with open(image_path, 'rb') as img_file:
                                        bot.send_photo(message.chat.id, img_file)
                                # После отправки всех изображений отправляем название папки
                                folder_name = os.path.basename(folder)
                                bot.send_message(message.chat.id, folder_name)

                elif "Сейчас скину информирующие презентации о компании" in sgen_text:
                    presentations = get_files("presentations")
                    if presentations:
                        for presentation in presentations:
                            with open(presentation, 'rb') as presentation_file:
                                bot.send_document(message.chat.id, presentation_file)

                elif "Сейчас скину видео о компании" in sgen_text:
                    videos = get_files("videos")
                    if videos:
                        for video in videos:
                            with open(video, 'rb') as video_file:
                                bot.send_document(message.chat.id, video_file)


            else:
                bot.send_message(message.chat.id, "Отправляю ваше сообщение админу.")
                notification_text = notify(message)
                for admin_id in check_admins()[0]:
                    bot.send_message(admin_id, notification_text)
    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)

if __name__ == "__main__":
    bot.infinity_polling()

