import os
import requests
import telebot
from time import sleep
from telebot import types
from config import TELEGRAM_BOT_API
from telebot.apihelper import ApiTelegramException
from youtube_utils import download_media, is_valid_youtube_url

user_data = {}
bot = telebot.TeleBot(TELEGRAM_BOT_API)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    if message.text.startswith('/'):
        return  # Do not process command messages in this handler.

    if is_valid_youtube_url(message.text):
        buttons_message_id = send_format_buttons(message.chat.id, message.text)
        user_data[message.chat.id] = {"link_message_id": message.message_id, "buttons_message_id": buttons_message_id}
    else:
        bot.send_message(message.chat.id, "Please send a valid YouTube link.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    format, youtube_url = call.data.split("|")
    if format in ["mp3", "mp4"]:
        processing_msg = bot.send_message(call.message.chat.id, f"Processing in {format.upper()} format...")

        media_filepath = download_media(youtube_url, format)

        # Check if the content is age-restricted
        if media_filepath == "age_restricted":
            # Retrieve the original message_id for the link from user_data
            original_link_message_id = user_data.get(call.message.chat.id, {}).get("link_message_id", None)

            if original_link_message_id:
                bot.send_message(call.message.chat.id, "This content is age-restricted and cannot be downloaded.",
                                 reply_to_message_id=original_link_message_id)
            else:
                # If for some reason the original message_id isn't available, send a normal message
                bot.send_message(call.message.chat.id, "This content is age-restricted and cannot be downloaded.")

            # Delete processing message and format selection buttons
            bot.delete_message(call.message.chat.id, processing_msg.message_id)

            if call.message.chat.id in user_data:
                buttons_message_id = user_data[call.message.chat.id].get("buttons_message_id")
                if buttons_message_id:
                    bot.delete_message(call.message.chat.id, buttons_message_id)

            return  # Exit the callback function early

        if media_filepath:
            send_media_to_user(bot, call.message.chat.id, media_filepath, format)
            os.remove(media_filepath)

            if call.message.chat.id in user_data:
                link_message_id = user_data[call.message.chat.id].get("link_message_id")
                buttons_message_id = user_data[call.message.chat.id].get("buttons_message_id")
            else:
                # You can either skip the current iteration or handle this scenario differently.
                return  # For now, I'm just skipping the current iteration.

            # The rest of your message deletion logic:
            try:
                if link_message_id:
                    bot.delete_message(call.message.chat.id, link_message_id)
            except ApiTelegramException as e:
                if "message to delete not found" not in str(e):
                    raise

            try:
                if buttons_message_id:
                    bot.delete_message(call.message.chat.id, buttons_message_id)
            except ApiTelegramException as e:
                if "message to delete not found" not in str(e):
                    raise

            sleep(1)
            try:
                bot.delete_message(call.message.chat.id, processing_msg.message_id)
            except ApiTelegramException as e:
                if "message to delete not found" not in str(e):
                    raise
        else:
            bot.send_message(call.message.chat.id, f"Couldn't process the video in {format.upper()} format.")



def send_format_buttons(chat_id, youtube_url):
    """Send a message with buttons for selecting file format."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton("MP3", callback_data=f"mp3|{youtube_url}")
    itembtn2 = types.InlineKeyboardButton("MP4", callback_data=f"mp4|{youtube_url}")
    markup.add(itembtn1, itembtn2)

    sent_message = bot.send_message(chat_id, "Choose a file format:", reply_markup=markup)
    return sent_message.message_id


def send_video_to_local_server(chat_id, filepath, bot_token):
    url = f"http://127.0.0.1:8081/bot{bot_token}/sendVideo"
    payload = {'chat_id': chat_id, 'supports_streaming': 'true'}
    with open(filepath, 'rb') as video_file:
        files = [('video', (os.path.basename(filepath), video_file, 'application/octet-stream'))]
        response = requests.post(url, data=payload, files=files)
    return response.text


def send_filename_message(bot, user_id, filename, format):
    name_without_extension = os.path.splitext(filename)[0]
    emoji = "🎶" if format == "mp3" else "📼" if format == "mp4" else ""
    bot.send_message(user_id, f"{emoji} {name_without_extension}")


def send_media_to_user(bot, user_id, media_filepath, format):
    if format == "mp3":
        with open(media_filepath, "rb") as media_file:
            bot.send_audio(user_id, media_file)
    elif format == "mp4":
        send_video_to_local_server(user_id, media_filepath, bot.token)
    else:
        bot.send_message(user_id, "Invalid format")

    send_filename_message(bot, user_id, os.path.basename(media_filepath), format)
