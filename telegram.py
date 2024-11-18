import telebot
from config import token
from methods import *
from HelperDB import *

if not os.path.exists('presentations'):
    os.makedirs('presentations')
if not os.path.exists('videos'):
    os.makedirs('videos')


dialog = []
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"}

bot = telebot.TeleBot(token)
admins = ['amida_f']
adminsChatId = ['1779183640']

#'f4est_f',
createDataBase("Def")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-данные-о-кабинках'))
def handle_add_cabins(message):
    if message.from_user.username in admins:
        bot.send_message(message.chat.id, "Введите информацию о кабинках")
        bot.register_next_step_handler(message, add_cabin)
def add_cabin(message):
    write_file("cabins", message.text)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-дату'))
def handle_add_date(message):
    if message.from_user.username in admins:
        data = message.text[len('!добавить-дату '):].strip()
        if data:
            result = save_data_to_db(data)
            if "Неверный формат даты" in result:
                bot.send_message(message.chat.id, result)
            else:
                sorted_dates = ", ".join(result)
                bot.send_message(message.chat.id, f"Дата добавлена. Все даты: {sorted_dates}")
        else:
            bot.send_message(message.chat.id, "Не была указана дата. Пожалуйста, введите её.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-дату'))
def handle_delete_date(message):
    if message.from_user.username in admins:
        data = message.text[len('!удалить-дату '):].strip()
        if data:
            result = delete_date_from_db(data)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Не была указана дата для удаления. Пожалуйста, введите её.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-файл'))
def handle_add_file(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте файл (презентацию или видео).")
    bot.register_next_step_handler(message, process_file)

def process_file(message):
    try:
        if message.document:
            file = message.document
            bot.send_message(message.chat.id, "Пожалуйста, введите название и расширение презентации.")
            bot.register_next_step_handler(message, process_file_name, file, 'presentations')
        elif message.video:
            file = message.video
            bot.send_message(message.chat.id, "Пожалуйста, введите название и расширение видео.")
            bot.register_next_step_handler(message, process_file_name, file, 'videos')
        else:
            bot.send_message(message.chat.id, "")
    except Exception as e:
        print(f"Error during file processing: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при проверке типа файла: {e}")

def process_file_name(message, file, file_type):
    try:
        user_file_name = message.text.strip()
        if user_file_name:
            if file_type == 'presentations':
                folder_path = 'presentations'
            elif file_type == 'videos':
                folder_path = 'videos'
            else:
                bot.send_message(message.chat.id, "Неверный тип файла.")
                return
            # Загружаем файл
            file_info = bot.get_file(file.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(folder_path, user_file_name)
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, f"Файл '{user_file_name}' успешно добавлен!")
        else:
            bot.send_message(message.chat.id, "Ошибка, вы не ввели название файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке файла: {e}")
        print(f"Error during file name processing: {e}")
@bot.message_handler(func=lambda message: message.text.startswith('!остановить-чат'))
def handle_stop_chat(message):
    bot.send_message(message.chat.id, "Введите chatId с которым хотите завершить чат.")
    bot.register_next_step_handler(message, process_stop_chat, message)
def process_stop_chat(message):
    change_waiting_flag_false(message.chatt.id)
    bot.send_message(message.chat.id, f"Чат с {message.chatt.id} завершен.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл'))
def handle_delete_file(message):
    presentations = get_presentations()
    videos = get_videos()
    all_files = presentations + videos
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
        else:
            bot.send_message(message.chat.id, "Отмена функции, введено неправильное название файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при удалении файла: {e}")
        print(f"Error during file deletion: {e}")


@bot.message_handler(content_types=["text"])
def welcome(message):
    add_user(message)
    try:
        print(message)
        if not message.text.startswith('!'):
            dialog = get_dialog_from_db(message.chat.id)
            if len(dialog) >= 20:
                dialog = dialog[20:]
            # Получаем все даты из базы данных
            all_dates = get_all_dates_from_db()
            # Формируем строку с датами для добавления в prompt
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            sgen_text = get_mess(message.text, f"Ты искуственный помощник технической поддержки компании 'Хуй в трусах', ты отвечаешь на вопросы по поводу компании ипо поводу брони, как отдел бронирования, отвечая занят день или нет, список занятых дат: {dates_text}, если в списке нету даты, значит нету брони. Сегодняшние дата и время - {getDateAndTime(message)} "
                                               f"Если пользователь хочет забронировать день, то ты должен у него спросить хочет ли он забронировать, после положительного ответа отправляй ему именно этот текст, никак не меняя его: 'Я вас направляю к админу, все подробности, а также бронирование можете обсудить с ним.' Но твоя основная роль информировать пользователя о наличии свободных дней." 
                                            f"Если пользователь хочет узнать информацию о компании,то ты ему рассказываешь про компанию, так же ты в конце будешь должен ему отправить именно этот текст, никак не меняя его: 'Сейчас отправлю вам уточняющие видео и презентации про компанию'", True, dialog)
            print("-" * 80)
            print(dates_text)
            dialog.append({"role": "user", "message": message.text})
            dialog.append({"role": "assistant", "message": sgen_text})
            save_dialog_to_db(message.chat.id, dialog)
            print("-" * 80)
            print(dialog)
            bot.send_message(message.chat.id, sgen_text)
            if "Я вас направляю к админу, все подробности, а также бронирование можете обсудить с ним." in sgen_text:
                change_waiting_flag_true(message.chat.id)
                for admin in adminsChatId:
                    bot.send_message(admin, f"Айди чата с пользователем : {message.chat.id}.\n"
                                            f"Сообщение пользователя : {message.text}\n"
                                            f"Чтобы ответить на это сообщение введите айди чата и ответное сообщение пользователю в таком формате:\n"
                                            f"6086449054 Сообщение: Мы приняли ваш запрос 19 ноября забронировано, можете отправить дополнительную информацию.")
            elif "Сейчас отправлю вам уточняющие видео и презентации про компанию" in sgen_text:
                try:
                    presentations = get_presentations()
                    for presentation in presentations:
                        with open(presentation, 'rb') as file:
                            bot.send_document(message.chat.id, file)
                except Exception as e:
                    print(f"Error sending presentations: {e}")
                    bot.send_message(message.chat.id, "Произошла ошибка при отправке презентаций.")
                try:
                    videos = get_videos()
                    for video in videos:
                        with open(video, 'rb') as file:
                            bot.send_video(message.chat.id, file)
                except Exception as e:
                    print(f"Error sending videos: {e}")
                    bot.send_message(message.chat.id, "Произошла ошибка при отправке видео.")
        #else:
            #if message.from_user.username in admins:
                #if message.text.startswith() in


    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)


if __name__ == "__main__":
    bot.infinity_polling()

