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

@bot.message_handler(func=lambda message: message.text.startswith('!ожидающие-ответа'))
def show_waiting_users(message):
    if message.from_user.username in admins:
        waiting_users = get_waiting_users()
        if waiting_users:
            waiting_list = "\n".join(map(str, waiting_users))
            bot.send_message(message.chat.id, f"Список ожидающих пользователей:\n{waiting_list}")
        else:
            bot.send_message(message.chat.id, "Нет пользователей, ожидающих ответа.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

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
            file = message.photo[-1]  # Берём наибольшую по размеру версию
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
            folder_path = 'styles'  # Здесь можно изменить на нужную папку
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Сохраняем описание в .txt файл
            description_path = os.path.join('descriptions', f"{user_file_name}.txt")
            if not os.path.exists('descriptions'):
                os.makedirs('descriptions')

            with open(description_path, 'w') as desc_file:
                desc_file.write(description)

            # Загружаем и сохраняем файл
            file_info = bot.get_file(file.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(folder_path, user_file_name)

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(message.chat.id, f"Файл '{user_file_name}' и описание успешно добавлены!")
        else:
            bot.send_message(message.chat.id, "Ошибка, вы не ввели описание файла.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при сохранении описания: {e}")
        print(f"Error during file description processing: {e}")


@bot.message_handler(func=lambda message: message.text.startswith('!остановить-чат'))
def handle_stop_chat(message):
    bot.send_message(message.chat.id, "Введите chatId с которым хотите завершить чат.")
    bot.register_next_step_handler(message, process_stop_chat)
def process_stop_chat(message):
    change_waiting_flag_false(message.text)
    bot.send_message(message.chat.id, f"Чат с {message.text} завершен.")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-файл'))
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

            # Формируем путь к файлу описания
            description_path = os.path.join('descriptions', f"{file_name}.txt")
            print(f"Попытка удалить описание по пути: {description_path}")  # Отладочное сообщение

            # Проверяем, существует ли файл описания, и удаляем его
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




def get_images():
    image_folder = 'styles'
    return [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

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
            dialog1 = get_dialog_from_db(message.chat.id)
            if len(dialog1) >= 20:
                dialog1 = dialog1[20:]
            # Получаем все даты из базы данных
            all_dates = get_all_dates_from_db()
            # Формируем строку с датами для добавления в prompt
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            sgen_text = get_mess(message.text, f"Ты искуственный помощник технической поддержки компании 'AbAi event', ты отвечаешь на вопросы по поводу компании ипо поводу брони, как отдел бронирования, отвечая занят день или нет, список занятых дат: {dates_text}, если в списке нету даты, значит нету брони. Сегодняшние дата и время - {getDateAndTime(message)} "
                                               f"Тексты про компанию: Компания, где технологии искусственного интеллекта превращают идеи в инновации и открывают новые возможности для вашего бизнеса. Мы создаем будущее уже сегодня!, второй текст:"
                                               f"Our software continues to connect with users worldwide! At our client’s event in Kazakhstan, we introduced our AI Photobooth software in partnership with @ai_fotokz ."
                                               f"Если пользователь хочет забронировать день, то ты должен у него спросить хочет ли он забронировать, после положительного ответа отправляй ему именно этот текст, никак не меняя его: 'Я вас направляю к админу, все подробности, а также бронирование можете обсудить с ним.' Но твоя основная роль информировать пользователя о наличии свободных дней." 
                                            f"Если пользователь хочет узнать информацию о компании,то ты ему рассказываешь про компанию, так же ты в конце будешь должен ему отправить именно этот текст, никак не меняя его: 'Сейчас отправлю вам уточняющие видео и презентации про компанию'", True, dialog1)
            print("-" * 80)
            print(dates_text)
            dialog1.append({"role": "user", "message": message.text})
            dialog1.append({"role": "assistant", "message": sgen_text})
            save_dialog_to_db(message.chat.id, dialog1)
            print("-" * 80)
            print(dialog1)
            bot.send_message(message.chat.id, sgen_text)
            if "Я вас направляю к админу, все подробности, а также бронирование можете обсудить с ним." in sgen_text:
                user_id = message.chat.id
                dialog_history = get_dialog_from_db(user_id)

                # Форматируем последние 10 сообщений
                if dialog_history:
                    last_10_messages = dialog_history[-10:]
                    formatted_history = "\n".join(
                        [f"{entry['role']}: {entry['message']}" for entry in last_10_messages]
                    )
                else:
                    formatted_history = "История сообщений отсутствует."

                # Формируем текст уведомления
                notification_text = (
                    f"Новый запрос от пользователя:\n"
                    f"Chat ID: {user_id}\n"
                    f"Сообщение: {message.text}\n\n"
                    f"Последние 10 сообщений:\n{formatted_history}\n\n"
                    f"Для ответа используйте формат:\n"
                    f"<chat_id> Сообщение: <текст ответа>"
                )

                # Отправляем уведомление каждому администратору
                for admin_id in adminsChatId:
                    bot.send_message(admin_id, notification_text)
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

                try:
                    bot.send_message(message.chat.id, "Также, смотрите какие стили у нас есть:")
                    images = get_images()

                    if images:
                        for image_path in images:
                            with open(image_path, 'rb') as img_file:
                                bot.send_photo(message.chat.id, img_file)

                except Exception as e:
                    print(f"Error sending styles: {e}")
        #else:
            #if message.from_user.username in admins:
                #if message.text.startswith() in


    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)

@bot.message_handler(func=lambda message: message.from_user.username in admins)
def handle_admin_reply(message):
    try:
        # Проверяем, соответствует ли сообщение формату
        if "Сообщение:" in message.text:
            parts = message.text.split("Сообщение:")
            user_id = parts[0].strip()  # ID пользователя
            reply_text = parts[1].strip()  # Текст сообщения

            # Проверяем, что ID пользователя — это число
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


if __name__ == "__main__":
    bot.infinity_polling()

