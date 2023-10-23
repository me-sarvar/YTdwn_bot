import os
import requests
import telebot
from time import sleep
from telebot import types
from config import TELEGRAM_BOT_API
from telebot.apihelper import ApiTelegramException
from pytube.exceptions import VideoUnavailable, PytubeError
from youtube_utils import download_media, is_valid_youtube_url, is_age_restricted

user_data = {}
bot = telebot.TeleBot(TELEGRAM_BOT_API)

def handle_message(message):
    if message.text.startswith('/'):
        return

    if is_valid_youtube_url(message.text):
        user_data[message.chat.id] = {"link_message_id": message.message_id}
        try:
            age_restricted = is_age_restricted(message.text)
            if age_restricted:
                bot.send_message(message.chat.id, "This content is age-restricted and cannot be downloaded.")
            elif age_restricted is None:
                bot.send_message(message.chat.id, "An error occurred. Please try again.")
            else:
                buttons_message_id = send_format_buttons(message.chat.id, message.text, message.message_id)
                user_data[message.chat.id].update({
                    "buttons_message_id": buttons_message_id,
                    "youtube_url": message.text
                })
        except (VideoUnavailable, PytubeError) as e:
            print(f"Error accessing the YouTube URL: {e}")
            bot.send_message(message.chat.id, "An error occurred. Please try again.")
            if message.chat.id in user_data:
                del user_data[message.chat.id]
    else:
        bot.send_message(message.chat.id, "Please send a valid YouTube link.")



def delete_processing_messages(chat_id):
    """Delete messages related to link processing."""
    user_state = user_data.get(chat_id)
    if not user_state or not isinstance(user_state, dict):
        return

    link_message_id = user_state.get("link_message_id")
    format_selection_message_id = user_state.get("format_selection_message_id")

    # Delete the messages
    if link_message_id:
        try:
            bot.delete_message(chat_id, link_message_id)
        except ApiTelegramException as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting link_message_id {link_message_id}: {e}")

    if format_selection_message_id:
        try:
            bot.delete_message(chat_id, format_selection_message_id)
        except ApiTelegramException as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting format_selection_message_id {format_selection_message_id}: {e}")

    # Clear the data.
    del user_data[chat_id]


def callback_query(call):
    """
    Handles callback queries (button clicks) from the user,
    processes the requested format, and sends the media to the user.
    """
    format, youtube_url = call.data.split("|")

    if format in ["mp3", "mp4"]:
        processing_msg = bot.send_message(call.message.chat.id, f"Processing in {format.upper()} format...",
                                          reply_to_message_id=call.message.reply_to_message.message_id)

        try:
            media_filepath = download_media(youtube_url, format)

            if media_filepath == "age_restricted":
                bot.send_message(call.message.chat.id, "This content is age-restricted and cannot be downloaded.")
            elif media_filepath:
                send_media_to_user(bot, call.message.chat.id, media_filepath, format)
                os.remove(media_filepath)

                # Attempting to delete the original message (YouTube link)
                original_link_message_id = call.message.reply_to_message.message_id
                print(
                    f"Attempting to delete link_message with ID {original_link_message_id} for chat {call.message.chat.id}")
                bot.delete_message(call.message.chat.id, original_link_message_id)

                # Attempting to delete the message with format buttons
                print(
                    f"Attempting to delete buttons_message with ID {call.message.message_id} for chat {call.message.chat.id}")
                bot.delete_message(call.message.chat.id, call.message.message_id)

                # Attempting to delete the processing message
                print(
                    f"Attempting to delete processing_msg with ID {processing_msg.message_id} for chat {call.message.chat.id}")
                bot.delete_message(call.message.chat.id, processing_msg.message_id)

            else:
                bot.send_message(call.message.chat.id, f"Couldn't process the video in {format.upper()} format.")

        except FileNotFoundError:
            bot.send_message(call.message.chat.id, "There was an error processing your request. Please try again.")
            print(f"File not found: {media_filepath}")

        except ApiTelegramException as e:
            print(f"Error deleting a message: {str(e)}")

    else:
        bot.send_message(call.message.chat.id, "Invalid format.")


def send_format_buttons(chat_id, youtube_url, reply_to_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton("MP3", callback_data=f"mp3|{youtube_url}")
    itembtn2 = types.InlineKeyboardButton("MP4", callback_data=f"mp4|{youtube_url}")
    markup.add(itembtn1, itembtn2)

    sent_message = bot.send_message(chat_id, "Choose a file format:", reply_markup=markup, reply_to_message_id=reply_to_id)
    return sent_message.message_id


def send_video_to_local_server(chat_id, filepath, bot_token):
    """
    Sends a video file to a local server for processing.

    :param chat_id: The ID of the chat where the video should be sent.
    :param filepath: The path to the video file.
    :param bot_token: The bot's token for authentication.
    :return: The response from the local server.
    """
    url = f"http://127.0.0.1:8081/bot{bot_token}/sendVideo"
    payload = {'chat_id': chat_id, 'supports_streaming': 'true'}
    with open(filepath, 'rb') as video_file:
        files = [('video', (os.path.basename(filepath), video_file, 'application/octet-stream'))]
        response = requests.post(url, data=payload, files=files)
    return response.text


def send_filename_message(bot, user_id, filename, format):
    """
    Sends a message to the user with the filename of the media they requested.

    :param bot: The bot instance.
    :param user_id: The ID of the user.
    :param filename: The name of the media file.
    :param format: The format of the media file (mp3/mp4).
    """
    name_without_extension = os.path.splitext(filename)[0]
    emoji = "🎶" if format == "mp3" else "📼" if format == "mp4" else ""
    bot.send_message(user_id, f"{emoji} {name_without_extension}")


def send_media_to_user(bot, user_id, media_filepath, format):
    """
    Sends the requested media (audio or video) to the user.

    :param bot: The bot instance.
    :param user_id: The ID of the user.
    :param media_filepath: The path to the media file.
    :param format: The format of the media file (mp3/mp4).
    """
    try:
        if format == "mp3":
            with open(media_filepath, "rb") as media_file:
                bot.send_audio(user_id, media_file)
        elif format == "mp4":
            send_video_to_local_server(user_id, media_filepath, bot.token)
        else:
            bot.send_message(user_id, "Invalid format")

        send_filename_message(bot, user_id, os.path.basename(media_filepath), format)

    except FileNotFoundError:
        bot.send_message(user_id, "There was an error processing your request. Please try again.")
        print(f"File not found: {media_filepath}")
    except Exception as e:
        bot.send_message(user_id, "There was an unexpected error. Please try again.")
        print(f"Error: {e}")

