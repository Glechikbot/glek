
# main_bot_with_task_system.py

import telebot
from flask import Flask
from threading import Thread
import datetime
import random
import time
import os

TOKEN = "7943821305:AAE1bhBzaJl2toCAlUgXF56samBQZTxAwGg"
USER_ID = 493019903

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! ✅"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

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

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == USER_ID:
        bot.send_message(message.chat.id, "🔔 Бот запущено! Пиши 'задачі' щоб подивитись список.")

@bot.message_handler(func=lambda msg: msg.text.strip().lower() == "задачі")
def show_main_tasks(message):
    if message.chat.id == USER_ID:
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

@bot.message_handler(func=lambda msg: "задача" in msg.text.lower() and "зроблена" in msg.text.lower())
def mark_task_done(message):
    if message.chat.id == USER_ID:
        all_tasks = load_main_tasks()
        done = load_done_tasks()

        raw_text = message.text.lower()
        possible = raw_text.replace("задача", "").replace("зроблена", "").strip()

        matched = None
        for task in all_tasks:
            if possible in task.lower():
                matched = task
                break

        if matched:
            done.add(matched)
            save_done_tasks(done)
            bot.send_message(message.chat.id, f"✅ Задача *{matched}* виконана!", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "🤷‍♂️ Не знайшов такої задачі.")

def scheduler():
    while True:
        now = datetime.datetime.now()
        if now.hour == 9:
            bot.send_message(USER_ID, "🌞 Добрий ранок! Готовий до нових звершень?")
        time.sleep(60 * 60)

if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=scheduler).start()
    bot.polling(none_stop=True)
