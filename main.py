import telebot
import subprocess
from config import TELEGRAM_BOT_API, APP_ID, HASH_ID
from telegram_utils import handle_message, callback_query, send_format_buttons, user_data
from youtube_utils import is_valid_youtube_url


def start_telegram_bot_api():
    tdlib_binary_path = "./telegram-bot-api/bin/telegram-bot-api"
    cmd = [tdlib_binary_path, '--api-id={}'.format(APP_ID), '--api-hash={}'.format(HASH_ID)]

    # Start the telegram bot api process
    process = subprocess.Popen(cmd)

    # Give it some time to start or use a method to check if it has successfully started
    import time
    time.sleep(10)  # Adjust as needed

    return process


bot = telebot.TeleBot(TELEGRAM_BOT_API)


@bot.message_handler(func=lambda message: True)
def on_message(message):
    handle_message(message)


@bot.callback_query_handler(func=lambda call: True)
def on_callback_query(call):
    callback_query(call)


if __name__ == "__main__":
    telegram_process = start_telegram_bot_api()
    try:
        bot.polling()
    finally:
        telegram_process.poll()
