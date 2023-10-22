import telebot
import subprocess
from config import TELEGRAM_BOT_API, APP_ID, HASH_ID
from telegram_utils import handle_message, callback_query

def start_telegram_bot_api():
    """
    Start the Telegram Bot API service using TDLib and return the process.
    """
    tdlib_binary_path = "./telegram-bot-api/bin/telegram-bot-api"
    cmd = [tdlib_binary_path, '--api-id={}'.format(APP_ID), '--api-hash={}'.format(HASH_ID)]

    # Start the telegram bot api process
    process = subprocess.Popen(cmd)

    # Give it some time to start or use a method to check if it has successfully started
    import time
    time.sleep(10)  # Adjust as needed

    return process

bot = telebot.TeleBot(TELEGRAM_BOT_API)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Sends a welcome message to the user when they initiate the bot.
    """
    user_name = message.from_user.first_name
    welcome_text = f"Hello, {user_name}! Welcome to the Telegram YouTube Downloader Bot. Send a valid YouTube link to start downloading."
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda message: True)
def on_message(message):
    """
    Handles all the incoming messages and processes them.
    """
    handle_message(message)

@bot.callback_query_handler(func=lambda call: True)
def on_callback_query(call):
    """
    Handles all the callback queries (like button clicks) made to the bot.
    """
    callback_query(call)

if __name__ == "__main__":
    telegram_process = start_telegram_bot_api()
    try:
        bot.polling()
    finally:
        telegram_process.poll()
