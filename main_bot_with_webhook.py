
# main_bot_with_webhook.py

import telebot
from flask import Flask, request
import os

TOKEN = "7943821305:AAE1bhBzaJl2toCAlUgXF56samBQZTxAwGg"
bot = telebot.TeleBot(TOKEN)

WEBHOOK_URL = "https://dashboard.render.com/web/srv-d0k4e57fte5s738bgqfg"

app = Flask(__name__)

def load_main_tasks():
    with open("main_tasks.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_done_tasks():
    if not os.path.exists("done_tasks.txt"):
        return set()
    with open("done_tasks.txt", "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_done_tasks(done_tasks):
    with open("done_tasks.txt", "w", encoding="utf-8") as f:
        for task in done_tasks:
            f.write(f"{task}\n")

def save_main_tasks(tasks):
    with open("main_tasks.txt", "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(f"{task}\n")

@app.route("/", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔔 Бот запущено! Пиши 'задачі' щоб подивитись список.")

@bot.message_handler(func=lambda msg: msg.text.strip().lower() == "задачі")
def show_main_tasks(message):
    all_tasks = load_main_tasks()
    done = load_done_tasks()
    lines = ["📝 *Список задач:*", ""]
    for task in all_tasks:
        if task in done:
            lines.append(f"~{task}~ ✅")
        else:
            lines.append(task)
    result = "\n".join(lines)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("++"))
def mark_done_double_plus(message):
    task_text = message.text.strip()[2:].strip()
    all_tasks = load_main_tasks()
    done = load_done_tasks()
    matched = None
    for task in all_tasks:
        if task_text.lower() in task.lower():
            matched = task
            break
    if matched:
        done.add(matched)
        save_done_tasks(done)
        bot.send_message(message.chat.id, f"✅ Задача *{matched}* виконана!", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Не знайшов такої задачі.")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("+"))
def add_new_task_plus(message):
    task_text = message.text.strip()[1:].strip()
    if not task_text:
        bot.send_message(message.chat.id, "⚠️ Напиши задачу після '+'.")
        return
    tasks = load_main_tasks()
    tasks.append(task_text)
    save_main_tasks(tasks)
    bot.send_message(message.chat.id, f"➕ Додано задачу: *{task_text}*", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text.strip().startswith("-"))
def delete_task_minus(message):
    task_text = message.text.strip()[1:].strip()
    tasks = load_main_tasks()
    new_tasks = [t for t in tasks if task_text.lower() not in t.lower()]
    if len(new_tasks) == len(tasks):
        bot.send_message(message.chat.id, "🤷‍♂️ Такої задачі не знайшов.")
    else:
        save_main_tasks(new_tasks)
        bot.send_message(message.chat.id, f"🗑️ Задачу з текстом *{task_text}* видалено.", parse_mode="Markdown")

if __name__ == "__main__":
    import requests
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
