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
createDataBase()
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"}

a = int(input())
if a == 1 : bot = telebot.TeleBot(token)
else: bot = telebot.TeleBot("6514999735:AAHO4Ypc87aYUZ8nbDTMp6Ny8ULepl6c3fE")
#bot = telebot.TeleBot(token)
dialog = []
info_about_commands = ("Информация о командах:\n!показать-вопросы\n!удалить-вопрос-ответ ?вопрос\n!добавить-вопрос-ответ ?вопрос !ответ\n!пользователи\n!админы\n!удалить-админа\n!добавить-админа\n!добавить-колонку <название_продолжение>\n!удалить-колонку <название_продолжение>\n!обновить-слот <дата> <колонка> <статус>"
                       "\n!показать-таблицу\n!забронировать <дата> <колонка>\n!добавить-данные-о-кабинках\n!ожидающие-ответа\n!добавить-дату\n!удалить-дату"
                       "\n!добавить-файл\n!остановить-чат\n!остановить-чат")
question_answer = create_str_ans()
print(question_answer)

@bot.message_handler(func=lambda message: message.text.startswith('!показать-вопросы') and message.from_user.username in check_admins()[1])
def handle_get_que(message):
    try:
        bot.send_message(message.chat.id, get_table_as_string())
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Не получилось удалить вопрос-ответ.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-вопрос-ответ') and message.from_user.username in check_admins()[1])
def handle_del_que_ans(message):
    try:
        content = message.text[len('!удалить-вопрос-ответ'):].strip()
        if '?' in content:
            question_part = content.strip('?').strip()
            bot.send_message(message.chat.id, delete_question(question_part))
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Не получилось удалить вопрос-ответ.")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-вопрос-ответ') and message.from_user.username in check_admins()[1])
def handle_add_que_ans(message):
    try:
        content = message.text[len('!добавить-вопрос-ответ'):].strip()
        if '?' in content and '!' in content:
            question_part, answer = content.split('!', 1)
            question = question_part.strip('?').strip()
            answer = answer.strip()
            bot.send_message(message.chat.id, add_question_answer(question, answer))
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Не получилось добавить вопрос-ответ.")

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

@bot.message_handler(func=lambda message: message.text.startswith('!открыть-файлы') and message.from_user.username in check_admins()[1])
def handle_display_files(message):
    print()


@bot.message_handler(func=lambda message: message.text.startswith('!добавить-файл1'))
def handle_add_file(message):
    bot.send_message(message.chat.id, f"Укажите в какую папку вы хотите добавить файл.\n{display_files()}")
    bot.register_next_step_handler(message, process_file1, os.getcwd())  # Передаем текущую директорию


def process_file1(message, current_path):
    try:
        if message.text.lower() == "выйти":
            bot.send_message(message.chat.id, "Выхожу из этой функции.")
            return

        target_path = os.path.join(current_path, message.text)

        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            bot.send_message(message.chat.id, "Введите корректное название папки или напишите <Выйти>.")
            bot.register_next_step_handler(message, process_file1, current_path)
            return

        check = check_folder_contents(target_path)
        bot.send_message(message.chat.id, check[0])

        if not check[1] and not check[2]:  # Папка пуста
            bot.send_message(message.chat.id, "Можете отправить файл, и я добавлю его в данную папку.")
            bot.register_next_step_handler(message, save_file, target_path)

        elif check[1] and check[2] is None:  # Есть подпапки, но нет файлов
            bot.register_next_step_handler(message, process_file1, target_path)

        elif not check[1] and check[2]:  # Есть только файлы
            bot.send_message(message.chat.id, "Можете отправить файл, и я добавлю его в данную папку или напишите <Выйти>.")
            bot.register_next_step_handler(message, save_file1, target_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке папки: {e}")

def save_file1(message, folder_path):
    try:
        if message.text:
            if message.text.lower() == 'выйти':
                bot.send_message(message.chat.id, 'Выхожу из функции.')
                return
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(folder_path, message.document.file_name)

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, f"Файл '{message.document.file_name}' успешно сохранен в папке '{folder_path}'.")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте документ.")
            bot.register_next_step_handler(message, save_file, folder_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении файла: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-файл'))
def handle_add_file(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте файл (презентацию, видео или фото).")
    bot.register_next_step_handler(message, process_file)

def process_file(message):
    try:
        print(message)
        if message.document:
            file = message.document
            save_file(file, 'presentations', message.chat.id)
        elif message.video:
            file = message.video
            save_file(file, 'videos', message.chat.id)
        elif message.photo:
            # Берем файл с наибольшим разрешением
            file = message.photo[-1]
            save_file(file, 'styles', message.chat.id)
        else:
            bot.send_message(message.chat.id, "Файл не распознан. Пожалуйста, отправьте документ, видео или фото.")
    except Exception as e:
        print(f"Error during file processing: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке файла: {e}")

def save_file(file, folder_path, chat_id):
    try:
        # Получаем информацию о файле
        file_info = bot.get_file(file.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Если у файла есть оригинальное имя (для документов), используем его
        if hasattr(file, 'file_name'):
            file_name = file.file_name
        else:
            # Если это фото или видео, генерируем имя
            file_name = f"{file.file_id}.jpg" if folder_path == 'styles' else f"{file.file_id}.mp4"

        # Убедимся, что папка существует
        os.makedirs(folder_path, exist_ok=True)

        # Полный путь для сохранения файла
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(chat_id, f"Файл '{file_name}' успешно сохранен в папке '{folder_path}'!")
        print(f"Файл сохранен по пути: {file_path}")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при сохранении файла: {e}")
        print(f"Error during file saving: {e}")


@bot.message_handler(func=lambda message: message.text.startswith('!остановить-чат') and message.from_user.username in check_admins()[1])
def handle_stop_chat(message):
    bot.send_message(message.chat.id, "Введите chatId с которым хотите завершить чат.")
    bot.register_next_step_handler(message, process_stop_chat)
def process_stop_chat(message):
    change_waiting_flag_false(message.text)
    bot.send_message(message.chat.id, f"Чат с {message.text} завершен.")

'''@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл') and message.from_user.username in check_admins()[1])
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
        print(f"Error during file deletion: {e}")'''
 

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
                print(get_language_by_user_id(message.chat.id))
                encoded_query = urllib.parse.quote(message.text)
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
                                                           f"Информационный текст в котором расписаны случаи, как на что отвечать и различная информация:: {company_text}"
                                                           f"Информация про компанию, имея данную информацию, ты отвечаешь на вопросы, если они поступят: {company_info}"
                                                           f"Если пользователь задаёт вопросы не по теме, например 'как установить виндовс' или что то в таком духе, то ты отправляешь ему эту ссылку, не добавляя от себя никакого текста, она поможет ему в решении вопроса:'https://google-poisk-vmesto-tebya.ru/?q={encoded_query}', только одну, но если пользователь просто спрашивает как дела или просто говорит привет, то ты отвечаешь по нормальному, как обычно отвечал бы"
                                                           f"Если пользователь хочет забронировать день (оно находится под цифрой 7, после уточняющего вопроса), то ты должен скинуть ему контактные данные менеджера продаж, затем спросить у пользователя данный текст: 'Забронировать услугу Фотозоны или Селфи-зеркал можно по телефону +7 707 33 88 591 (WhatsApp, Telegram), через Инстаграмм https://www.instagram.com/abai.event', после положительного ответа отправляй ему именно этот текст никак не меняя его:Я вас направляю к менеджеру продаж, все подробности, а также бронирование можете обсудить с ним,если хотите завершить чат с админом введите !завершить-чат', так же скидываешь текст в котором будут ситуативные вопросы и вот там будет ответНо твоя основная роль информировать пользователя о наличии свободных дней."
                                                           f"Если пользователь хочет узнать информацию о компании, то ты ему рассказываешь про компанию, так же спрашиваешь хочет ли пользователь получить больше информации про компанию, если он скажет, что хочет, то ты будешь спросить у него информацию из данного текста: '{question_text}'"
                                                           f"Если пользователь говорит, что хочет узнать про стили обработки ИИ(оно находится под цифрой 1, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Стиль обработки фото вы можете выбрать самостоятельно из списка тем, которые уже есть, либо придумать свой Индивидуальный стиль, который наша нейросеть подготовит и реализует специально для Вас.'"
                                                           f"Если пользователь говорит, что хочет узнать про примеры фотографий до/после(оно находится под цифрой 2, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас отправлю примеры фото с наложенным ИИ, либо же вы можете более подробно ознакомиться с ними в нашем Инстаграме https://www.instagram.com/abai.event', ссылку отправляешь только один раз и без лишних спец знаков, просто ссылку"
                                                           f"Если пользователь говорит, что хочет узнать про фотобудки и селфи зеркала(оно находится под цифрой 6, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'На данный момент имеются 2 фотобудки и 2 селфи зеркала:'"
                                                           f"Если пользователь говорит, что хочет посмотреть презентации о компании(оно находится под цифрой 8, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас скину информирующие презентации о компании'"
                                                           f"Если пользователь говорит, что хочет посмотреть видео о компании(оно находится под цифрой 9, после уточняющего вопроса), то ты отправляешь именно этот текст, никак не меняя его: 'Сейчас скину видео о компании'"
                                                           f"Если пользователь хочет сменить язык на английский пиши ему этот текст на английском, Смена языка на английский, Тілді қазақ тіліне ауыстыру, Switching language to English.. Также делай с казахским и русским и пиши смену языка на соответствующих языках. Если же у пользователя не установлен язык, спроси на каком языке ему удобно общаться, данные о его языке: {get_language_by_user_id(message.chat.id)}. Все запросы и команды ты обрабатываешь на языке пользователя. Ты можешь общаться только на русском, казахском и английском, в иных случаях говори что не поддерживаешь"
                                                           f"Если с тобой начинают говорить на другом языке отличного от установленного, поинтересуйся о смене языка пользователя",True, dialog1)
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

