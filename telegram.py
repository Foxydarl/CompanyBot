import telebot
from config import token
from methods import *

dialog = []
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDcyNDg2ODAtNjMzMC00MmJiLWE3NGItMjlkNTQyYjJiNzFhIiwidHlwZSI6ImFwaV90b2tlbiJ9.y_1ufwKGnOWSZqAFgDJO0h99aoOXZ9dUZDKyNBvw6ks"}

bot = telebot.TeleBot(token)
admins = ['f4est_f', 'amida_f']


@bot.message_handler(func=lambda message: message.text.startswith('!добавить-дату'))
def handle_add_date(message):
    if message.from_user.username in admins:
        data = message.text[len('!добавить-дату '):].strip()
        if data:
            result = save_data_to_db(data)
            if "Неверный формат даты" in result:
                bot.send_message(message.chat.id, result)  # Если ошибка формата, отправляем сообщение
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

@bot.message_handler(content_types=["text"])
def welcome(message):
    try:

        if not message.text.startswith('!'):
            # Получаем все даты из базы данных
            all_dates = get_all_dates_from_db()
            # Формируем строку с датами для добавления в prompt
            dates_text = "\n".join(all_dates) if all_dates else "Нет доступных дат."
            sgen_text = get_mess(message.text, f"Ты искуственный помощник технической поддержки компании 'Хуй в трусах', ты отвечаешь на вопросы по поводу брони, как отдел бронирования, отвечая занят день или нет, список занятых дат: {dates_text}, если в списке нету даты, значит нету брони", False, [])
            print("-" * 80)
            print(dates_text)
            bot.send_message(message.chat.id, sgen_text)
    except TypeError as e:
        error_text = e.args[0]
        print("-" * 80)
        print(error_text)
        bot.send_message(message.chat.id, error_text)
        bot.send_message(message.chat.id, "Вот ошибка, которая вышла")




if __name__ == "__main__":
    bot.infinity_polling()

