# -*- coding: utf-8 -*-
import telebot
from config import token
from methods import *
from HelperDB import *
import urllib.parse


with open("text.txt", "r", encoding="utf-8") as file:
                    company_text = file.read().strip()
with open("company_info.txt", "r", encoding="utf-8") as file:
                    company_info = file.read().strip()
if not os.path.exists('presentations'):
    os.makedirs('presentations')
if not os.path.exists('videos'):
    os.makedirs('videos')

dialog = []
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"}

bot = telebot.TeleBot(token)
info_about_commands = ("Информация о командах:\n!пользователи\n!админы\n!удалить-админа\n!добавить-админа\n!добавить-колонку <название_продолжение>\n!удалить-колонку <название_продолжение>\n!обновить-слот <дата> <колонка> <статус>"
                       "\n!показать-таблицу\n!забронировать <дата> <колонка>\n!добавить-данные-о-кабинках\n!ожидающие-ответа\n!добавить-дату\n!удалить-дату"
                       "\n!добавить-файл\n!остановить-чат\n!остановить-чат")

createDataBase()

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

@bot.message_handler(func=lambda message: message.text.startswith('!обновить-слот') and message.from_user.username in check_admins()[1])
def handle_update_slot(message):
    try:
        _, date, column_name, status = message.text.split(" ", 3)
        result = update_slot(date, column_name, status)
    except ValueError:
        result = "⚠️ Используйте: !обновить-слот <дата> <колонка> <статус>"
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

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-файл') and message.from_user.username in check_admins()[1])
def handle_add_file(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте файл (презентацию, видео или изображение).")
    bot.register_next_step_handler(message, process_file)

def process_file(message):
    try:
        if message.document:
            file = message.document
            bot.send_message(message.chat.id, "Пожалуйста, введите название и расширение файла.")
            bot.register_next_step_handler(message, process_file_name, file)
        elif message.video:
            file = message.video
            bot.send_message(message.chat.id, "Пожалуйста, введите название и расширение видео.")
            bot.register_next_step_handler(message, process_file_name, file)
        elif message.photo:
            file = message.photo[-1]
            bot.send_message(message.chat.id, "Пожалуйста, введите название и расширение изображения.")
            bot.register_next_step_handler(message, process_file_name, file)
        else:
            bot.send_message(message.chat.id, "Ошибка, вы отправили неподдерживаемый тип данных.")
    except Exception as e:
        print(f"Error during file processing: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при проверке типа файла: {e}")


def process_file_name(message, file):
    try:
        user_file_name = message.text.strip()
        if user_file_name:
            bot.send_message(message.chat.id, "Пожалуйста, введите описание файла.")
            bot.register_next_step_handler(message, process_file_description, file, user_file_name)
        else:
            bot.send_message(message.chat.id, "Ошибка, вы не ввели название файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке имени файла: {e}")
        print(f"Error during file name processing: {e}")


def process_file_description(message, file, user_file_name):
    try:
        description = message.text.strip()
        if description:
            folder_path = 'styles'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            description_path = os.path.join('descriptions', f"{user_file_name}.txt")
            if not os.path.exists('descriptions'):
                os.makedirs('descriptions')

            with open(description_path, 'w') as desc_file:
                desc_file.write(description)

            file_info = bot.get_file(file.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(folder_path, user_file_name)

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, f"Файл '{user_file_name}' и описание успешно добавлены!")
        else:
            bot.send_message(message.chat.id, "Ошибка, вы не ввели описание файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке файла: {e}")
        print(f"Error during file name processing: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!остановить-чат') and message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    bot.send_message(message.chat.id, "Введите chatId с которым хотите завершить чат.")
    bot.register_next_step_handler(message, process_stop_chat)
def process_stop_chat(message):
    change_waiting_flag_false(message.text)
    bot.send_message(message.chat.id, f"Чат с {message.text} завершен.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл') and message.from_user.username in check_admins()[1])
def handle_delete_file(message):
    presentations = get_presentations()
    videos = get_videos()
    images = get_images()
    all_files = presentations + videos + images

    if all_files:
        file_names = "\n".join([os.path.basename(f) for f in all_files])
        bot.send_message(message.chat.id, f"Доступные файлы для удаления:\n{file_names}")
        bot.send_message(message.chat.id, "Пожалуйста, введите название файла с расширением для удаления.")
        bot.register_next_step_handler(message, process_delete_file, all_files)
    else:
        bot.send_message(message.chat.id, "Нет доступных файлов для удаления.")

def process_delete_file(message, all_files):
    try:
        file_name = message.text.strip()
        file_path = None

        for file in all_files:
            if os.path.basename(file) == file_name:
                file_path = file
                break

        if file_path:
            os.remove(file_path)
            bot.send_message(message.chat.id, f"Файл '{file_name}' был успешно удален.")

            description_path = os.path.join('descriptions', f"{file_name}.txt")
            print(f"Попытка удалить описание по пути: {description_path}")

            if os.path.exists(description_path):
                os.remove(description_path)
                bot.send_message(message.chat.id, f"Описание для файла '{file_name}' также было удалено.")
            else:
                bot.send_message(message.chat.id, f"Описание для файла '{file_name}' не найдено.")
        else:
            bot.send_message(message.chat.id, "Отмена функции, введено неправильное название файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении файла: {e}")
        print(f"Error during file deletion: {e}")



def process_delete_file(message, all_files):
    try:
        file_name = message.text.strip()
        file_path = None
        for file in all_files:
            if os.path.basename(file) == file_name:
                file_path = file
                break
        if file_path:
            os.remove(file_path)
            bot.send_message(message.chat.id, f"Файл '{file_name}' был успешно удален.")
        else:
            bot.send_message(message.chat.id, "Отмена функции, введено неправильное название файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении файла: {e}")
        print(f"Error during file deletion: {e}")


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
                with open("question.txt", "r", encoding="utf-8") as file1:
                    question_text = file1.read().strip()

                encoded_query = urllib.parse.quote(message.text)
                sgen_text = get_mess(message.text, f"Ты искуственный помощник технической поддержки компании 'AbAi event', отвечающий на языке, смотря на каком с тобой общаются,"
                                                           f"ты отвечаешь на вопросы по поводу компании и по поводу брони, так же ты просто разговариваешь с пользователем если он ведёт с тобой диалог, если человек спрашивает про бронь, ты отвечаешь занят день или нет, если занят, то какими будками, список занятых дат,"
                                                           f"а также колонок: {check_dates_and_cabins()}, если в списке нету даты, значит нету брони, а также пиши пользователю свободные кабинки в виде списка если дата свободна. Сегодняшние дата и время - {getDateAndTime(message)} "
                                                           f"Информационный текст в котором расписаны случаи, как на что отвечать и различная информация:: {company_text}"
                                                           f"Информация про компанию, имея данную информацию, ты отвечаешь на вопросы, если они поступят: {company_info}"
                                                           f"На глупые вопросы или вопросы не по поводу компании или вопросы которые не по теме диалога ты отправляешь эту ссылку, никак просто не меняя её, не добавляя никакого текста: 'https://google-poisk-vmesto-tebya.ru/?q={encoded_query}', только одну, но если пользователь просто спрашивает как дела или просто говорит привет, то ты отвечаешь по нормальному, как обычно отвечал бы"
                                                           f"Если пользователь хочет забронировать день, то ты должен скинуть ему контактные данные менеджера продаж, затем спросить у пользователя хочет ли он забронировать в телеграмме напрямую, после положительного ответа отправляй ему именно этот текст никак не меняя его:Я вас направляю к менеджеру продаж, все подробности, а также бронирование можете обсудить с ним,если хотите завершить чат с админом введите !завершить-чат. Но твоя основная роль информировать пользователя о наличии свободных дней.'"
                                                           f"Если пользователь хочет узнать информацию о компании, то ты ему рассказываешь про компанию, так же спрашиваешь хочет ли пользователь получить больше информации про компанию, если он скажет, что хочет, то ты будешь спросить у него информацию из данного текста: '{question_text}'"
                                                           f"Если пользователь говорит, что хочет узнать про стили обработки ИИ(оно находится под цифрой 1, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас, отправлю стили обработки ИИ для вашего ознакомления'", True, dialog1)
                print("-" * 80)
                print(dates_text)
                dialog1.append({"role": "user", "message": message.text})
                dialog1.append({"role": "assistant", "message": sgen_text})
                save_dialog_to_db(message.chat.id, dialog1)
                print("-" * 80)
                print(dialog1)
                bot.send_message(message.chat.id, sgen_text)
                if "Я вас направляю к менеджеру продаж, все подробности, а также бронирование можете обсудить с ним." in sgen_text:
                    notification_text = notify(message)
                    for admin_id in check_admins()[0]:
                        bot.send_message(admin_id, notification_text)
                elif "Сейчас, отправлю стили обработки ИИ для вашего ознакомления" in sgen_text:
                    try:
                        images = get_images('styles')
                        if images:
                            for image_path in images:
                                with open(image_path, 'rb') as img_file:
                                    bot.send_photo(message.chat.id, img_file)
                                    bot.send_message(message.chat.id, os.path.basename(image_path))
                            bot.send_message(message.chat.id, "Не нашли подходящий? \nМы можем разработать индивидуальный стиль")
                    except Exception as e:
                        print(f"Error sending styles: {e}")
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

