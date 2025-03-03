@bot.message_handler(func=lambda message: message.text.startswith('!вопрос-ответ') and message.from_user.QA in check_QA()[1])
def handle_show_QA(message):
    formatted_table = format_QA_table()
    bot.send_message(message.chat.id, formatted_table, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('!удалить-вопрос-ответ') and message.from_user.QA in check_QA()[1])
def handle_delete_QA_cmd(message):
    try:
        QA = message.text.split(" ", 1)[1]
        result = delete_QA(QA)
    except Exception:
        result = "⚠️ Не получилось удалить вопрос-ответ."
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text.startswith('!добавить-вопрос-ответ') and message.from_user.QA in check_QA()[1])
def handle_add_QA_cmd(message):
    try:
        QA = message.text.split(" ", 1)[1]
        result = add_QA(QA)
    except Exception as e:
        print(f"Error: {e}")
        result = "⚠️ Не получилось добавить вопрос-ответ."
    bot.reply_to(message, result)