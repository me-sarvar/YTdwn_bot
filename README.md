# Telegram YouTube Downloader Bot

A Telegram bot that allows users to download media from YouTube in different formats.

## Try the Bot Live

Experience the bot live on Telegram! Click [here](https://t.me/ytdwn_bot) or search for `@ytdwn_bot` on Telegram.


## Features

- Allows users to download media from YouTube as MP3 or MP4.
- Provides inline buttons for users to select their desired format.
- Validates YouTube URLs.
- Sends a welcome message upon starting the bot.
- **Handles age-restricted content and notifies the user if a video is not accessible due to age restrictions.**

## Dependencies

- `requests`
- `os`
- `telebot`
- `time`
- `pytube`
- `re`
- `configparser`
- `subprocess`

## Configuration

1. Create a `config.ini` file in the root directory with the following structure:

```
[TELEGRAM]
API_TOKEN = <Your_Telegram_Bot_Token>
API_ID = <Your_API_ID>
API_HASH = <Your_API_HASH>
VERBOSITY = <Your_VERBOSITY_Level>
```

2. Replace placeholders with your respective values.

## Installation

For the Telegram bot to function correctly, you'll need the [telegram-bot-api](https://github.com/tdlib/telegram-bot-api). Visit the [telegram-bot-api GitHub repository](https://github.com/tdlib/telegram-bot-api) to see how to install and set it up.

## Usage

1. Start the bot using your desired method.
2. Send a `/start` command to your bot on Telegram.
3. Upon receiving the welcome message, send a valid YouTube link.
4. Choose the desired format using the inline buttons.
5. Wait for the bot to process and send the media.
6. **If the video is age-restricted, the bot will notify you and will not be able to download the media.**

## Future Improvements

- Implement more error handling for invalid links.
- Support for more media formats.
- Implement a more interactive user experience.
