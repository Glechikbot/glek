
import os
import json
import telebot
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "7943821305:AAE1bhBzaJl2toCAlUgXF56samBQZTxAwGg"
WEBHOOK_URL = "https://glek.onrender.com/"

# Авторизація Google Sheets через ENV
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_data = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)

SHEET_NAME = "TaskBot"
SHEET_TAB = "Аркуш1"
sheet = client.open(SHEET_NAME).worksheet(SHEET_TAB)

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

@app.route("/", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

def get_tasks():
    return sheet.get_all_records()

def add_task(text):
    sheet.append_row([text, "FALSE"])

def delete_task(text):
    records = sheet.get_all_values()
    for idx, row in enumerate(records[1:], start=2):
        if text.lower() in row[0].lower():
            sheet.delete_rows(idx)
            return True
    return False

def mark_task_done(text):
    records = sheet.get_all_values()
    for idx, row in enumerate(records[1:], start=2):
        if text.lower() in row[0].lower():
            sheet.update_cell(idx, 2, "TRUE")
            return row[0]
    return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "🔗 Бот з Google Sheets готовий! Пиши 'задачі' щоб подивитись.")

@bot.message_handler(func=lambda msg: msg.text.strip().lower() == "задачі")
def list_tasks(message):
    try:
        rows = get_tasks()
        if not rows:
            bot.send_message(message.chat.id, "⚠️ Задач поки немає.")
            return
        result = ["📝 *Список задач:*", ""]
        for r in rows:
            done = str(r["Done"]).strip().lower() == "true"
            task = r["Task"].replace("-", "\-").replace(".", "\.").replace("(", "\(").replace(")", "\)").replace("!", "\!").replace("~", "\~")
            line = f"~{task}~ ✅" if done else task
            result.append(line)
        bot.send_message(message.chat.id, "\n".join(result), parse_mode="MarkdownV2")
    except Exception as e:
        print("🔥 Error in 'задачі':", e)
        bot.send_message(message.chat.id, "❌ Помилка при завантаженні задач.")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("++"))
def done_task(message):
    text = message.text.strip()[2:].strip()
    task = mark_task_done(text)
    if task:
        bot.send_message(message.chat.id, f"✅ Задача *{task}* виконана!", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Не знайшов такої задачі.")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("+"))
def add_task_handler(message):
    text = message.text.strip()[1:].strip()
    add_task(text)
    bot.send_message(message.chat.id, f"➕ Додано задачу: *{text}*", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("-"))
def delete_task_handler(message):
    text = message.text.strip()[1:].strip()
    if delete_task(text):
        bot.send_message(message.chat.id, f"🗑️ Задачу з текстом *{text}* видалено.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Такої задачі не знайшов.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
